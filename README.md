<div style="text-align: center;">
  <img src="https://www.uvlhub.io/static/img/logos/logo-light.svg" alt="Logo">
</div>

# uvlhub.io

Repository of feature models in UVL format integrated with Zenodo and flamapy following Open Science principles - Developed by DiversoLab

## Official documentation

You can consult the official documentation of the project at [docs.uvlhub.io](https://docs.uvlhub.io/)

## Puesta en marcha (desarrollo)

1. `cp .env.docker.example .env`
2. `docker compose -f docker/docker-compose.dev.yml up -d`
3. Abrir `http://localhost`
4. Tests: `docker exec -it web_app_container bash` y después `rosemary test`
