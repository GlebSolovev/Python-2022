**How to use Dockerfile:**
```bash
# from hw_2 folder
docker build . -t gen_pdf
docker run -td gen_pdf:latest

# get gen_pdf:latest container id from docker container ls
# let it be: 06c6629273a7
# host_file_path - desired path to output.pdf on host 
docker cp 06c6629273a7:hw_2/artifacts/output.pdf host_file_path
# resulting pdf file - host_file_path
```