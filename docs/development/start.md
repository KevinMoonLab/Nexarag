# Development

## 1. Clone the Repository

```bash
git clone https://github.com/KevinMoonLab/Nexarag.git
cd Nexarag
```

## 2. Docker Compose

Use the appropriate file for your hardware, from `docker/dev`:

* **CPU:**

  ```bash
  docker compose -f docker-compose.cpu.yml up -d
  ```
* **GPU:**

  ```bash
  docker compose -f docker-compose.gpu.yml up -d
  ```
* **MacOS:**
  ```bash
  docker compose -f docker-compose.mac.yml up -d
  ```

## 3. Configure dev environment
* [Frontend](./frontend.md)
* [Backend](./backend.md)
