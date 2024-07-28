# Set up project :pushpin:

## :heavy_check_mark: Install pyenv
https://github.com/pyenv/pyenv-installer
- Windows (Powershell)
```sh
git clone https://github.com/pyenv-win/pyenv-win.git %USERPROFILE%\.pyenv
````
Add '%USERPROFILE%\.pyenv\pyenv-win\bin and %USERPROFILE%\.pyenv\pyenv-win\shims' to  PATH

## :heavy_check_mark: Install poetry
https://python-poetry.org/docs/#installing-with-the-official-installer
- Linux, macOS, Windows (WSL)
```sh
curl -sSL https://install.python-poetry.org | python3 -
````
- Windows (Powershell)
```sh
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
````
```sh
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
````

## :heavy_check_mark: Install Docker Desktop
https://www.docker.com/products/docker-desktop/
- Create qdrant image
https://hub.docker.com/r/qdrant/qdrant
````sh
docker pull qdrant/qdrant
````
````sh
docker run -d -p 6333:6333 qdrant/qdrant
````

## :heavy_check_mark: .env variables
````sh
OPENAI_API_KEY= xx
DATA_PATH=C:\\Users\\xx\\Desktop\\wbs-chatbot\\wbs_chatbot\\data\\products-Neptun.csv
CLEANED_DATA_PATH=C:\\Users\\xx\\Desktop\\wbs-chatbot\\wbs_chatbot\\data\\cleaned_data.csv
````
