#!/usr/bin/env bash

# Actualizar pip
pip install --upgrade pip

# Instalar ffmpeg
apt-get update && apt-get install -y ffmpeg

# Instalar todas las dependencias incluyendo gunicorn
pip install -r requirements.txt
