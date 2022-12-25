#!/usr/bin/env bash

# You need to have a file that sets up environment variables:
# Example file content for setenv.sh:
#
# MP3MDF_INPUT_FOLDER=/home/youruser/music_to_analyze
# MP3MDF_OUTPUT_FOLDER=/multimedia/your_music_files
# GENIUS_ACCESS_TOKEN=YOUR_ACCESS_TOKEN_FOR_GENIUS
# export MP3MDF_INPUT_FOLDER
# export MP3MDF_OUTPUT_FOLDER
# export GENIUS_ACCESS_TOKEN
source setenv.sh

NOCOLOR='\033[0m'
GREEN='\033[0;32m'

CONTAINER_NAME="mp3mdf"

echo -e "${GREEN}Cleaning up containers and images (if existing)${NOCOLOR}"
docker container stop   "${CONTAINER_NAME}"
docker container rm  -f "${CONTAINER_NAME}"
docker image     rm  -f "${CONTAINER_NAME}"

echo -e "${GREEN}Building container image for >${CONTAINER_NAME}< ${NOCOLOR}"
docker image build -t ${CONTAINER_NAME}:latest -f "Dockerfile"  .

echo -e "${GREEN}Starting container >${CONTAINER_NAME}< ${NOCOLOR}"

if [[ $MP3MDF_INPUT_FOLDER ]] && [[ $MP3MDF_OUTPUT_FOLDER ]]; then
    echo -e "${GREEN} - Mounting input  folder >${MP3MDF_INPUT_FOLDER}< ${NOCOLOR}"
    echo -e "${GREEN} - Mounting output folder >${MP3MDF_OUTPUT_FOLDER}< ${NOCOLOR}"

    docker container run --rm  -it -d --name "${CONTAINER_NAME}" \
                            -e GENIUS_ACCESS_TOKEN=${GENIUS_ACCESS_TOKEN} \
                            --mount type=bind,source="${MP3MDF_INPUT_FOLDER}",target="/${CONTAINER_NAME}/data/input/" \
                            --mount type=bind,source="${MP3MDF_OUTPUT_FOLDER}",target="/${CONTAINER_NAME}/data/output/" \
                            "${CONTAINER_NAME}:latest"
else
    echo "Environment variable MP3MDF_INPUT_FOLDER or MP3MDF_OUTPUT_FOLDER not set!"
    echo "Will create container without mounting folders."
    docker container run --rm  -it -d --name "${CONTAINER_NAME}" "${CONTAINER_NAME}:latest"
fi

