import codecs
import time
from datetime import datetime
from multiprocessing import Process, Queue, Value, Pipe, Condition, Lock
from multiprocessing.connection import Connection
from threading import Thread

STOP_LINE = "stop"
PROCESS_A_DELAY_SECS = 5


def a_task(stdin_queue: Queue, stdin_queue_condition: Condition, exiting: Value, ab_conn: Connection, ab_condition: Condition):
    while not exiting.value:
        stdin_queue_condition.acquire()
        stdin_queue_condition.wait_for(lambda: exiting.value or not stdin_queue.empty())
        stdin_queue_condition.release()
        if exiting.value:
            break
        message = stdin_queue.get()
        lowered_message = message.lower()

        ab_conn.send(lowered_message)
        ab_condition.acquire()
        ab_condition.notify()
        ab_condition.release()

        time.sleep(PROCESS_A_DELAY_SECS)

    while not stdin_queue.empty():
        stdin_queue.get()


def b_task(exiting: Value, ab_conn: Connection, ab_condition: Condition, out_conn: Connection,
           out_condition: Condition):
    while not exiting.value:
        ab_condition.acquire()
        ab_condition.wait_for(lambda: exiting.value or ab_conn.poll())
        ab_condition.release()
        if exiting.value:
            return
        message = ab_conn.recv()
        encoded_message = codecs.encode(message, "rot_13")

        out_conn.send(encoded_message)
        out_condition.acquire()
        out_condition.notify()
        out_condition.release()


def stdin_task(stdin_queue: Queue, stdin_queue_condition: Condition):
    while True:
        line = input()
        print(line + " < stdin " + datetime.now().strftime("%H:%M:%S"))
        if line == STOP_LINE:
            return
        stdin_queue.put(line)
        stdin_queue_condition.acquire()
        stdin_queue_condition.notify()
        stdin_queue_condition.release()


def stdout_task(exiting: Value, out_conn: Connection, out_condition: Condition):
    while not exiting.value:
        out_condition.acquire()
        out_condition.wait_for(lambda: exiting.value or out_conn.poll())
        out_condition.release()
        if exiting.value:
            return
        message = out_conn.recv()
        print(message + " < stdout " + datetime.now().strftime("%H:%M:%S"))


def main():
    stdin_queue = Queue()
    stdin_queue_condition = Condition(Lock())
    exiting = Value('i', False)

    parent_ab_conn, child_ab_conn = Pipe()
    ab_condition = Condition(Lock())

    parent_out_conn, child_out_conn = Pipe()
    out_condition = Condition(Lock())

    process_a = Process(target=a_task, args=(stdin_queue, stdin_queue_condition, exiting, parent_ab_conn, ab_condition))
    process_b = Process(target=b_task, args=(exiting, child_ab_conn, ab_condition, parent_out_conn, out_condition))

    stdin_thread = Thread(target=stdin_task, args=(stdin_queue, stdin_queue_condition))
    stdout_thread = Thread(target=stdout_task, args=(exiting, child_out_conn, out_condition))

    # start processes, THEN! local threads
    process_a.start()
    process_b.start()

    stdin_thread.start()
    stdout_thread.start()

    # wait for STOP_LINE
    stdin_thread.join()
    exiting.value = True

    # wake up all waiting
    stdin_queue_condition.acquire()
    stdin_queue_condition.notify()
    stdin_queue_condition.release()

    ab_condition.acquire()
    ab_condition.notify()
    ab_condition.release()

    out_condition.acquire()
    out_condition.notify()
    out_condition.release()

    # join processes, then left local threads
    process_a.join()
    process_b.join()

    stdout_thread.join()


if __name__ == '__main__':
    main()
