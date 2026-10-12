# BookNest: Procedure (Experiments 1 to 12)

Project: **BookNest, Campus Library Reservation System**
Stack: Flask · SQLite · Git/GitHub · Jenkins · Docker · Pytest · Ansible
Ports: app 5002, Jenkins 9091 (same setup as your Digital Canteen lab).

---

## STEP 1: Create the project folder (Exp 4, 8, 9)

Copy the `booknest` folder to your machine, then:

```bash
cd booknest
```

Run locally once to check:

```bash
pip install -r requirements.txt
python -m pytest test_app.py
python app.py
```
Open http://localhost:5000

---

## STEP 2: Git + GitHub (Exp 1, 2)

Create an empty repo named `BookNest` on GitHub, then:

```bash
git init
git add .
git commit -m "Initial BookNest application"
git branch -M master
git remote add origin https://github.com/<your-username>/BookNest.git
git push -u origin master
```

Show fetch and pull:

```bash
git fetch origin
git pull origin master
```

---

## STEP 3: Branching and merging (Exp 3)

```bash
git checkout -b feature/search-ui
```
Make a small edit (for example change the hero text in `templates/index.html`):

```bash
git add .
git commit -m "Update hero text on home page"
git checkout master
git merge feature/search-ui
git push origin master
git branch
git log --oneline --graph
```
(Screenshot the `git log --graph` output as merge evidence.)

---

## STEP 4: Docker image and container (Exp 7, 8, 9)

```bash
docker build -t booknest-ci .
docker run --rm booknest-ci python -m pytest test_app.py -v
docker run -d --name booknest-test -p 5002:5000 booknest-ci
docker ps
```
Open http://localhost:5002, then clean up:

```bash
docker rm -f booknest-test
```

---

## STEP 5: Ansible container (Exp 11, 12)

Reuse your existing Ansible lab container `ansible-docker-lab` (the one from your Digital Canteen project). Copy the playbook files into it:

```bash
docker cp ansible/deploy.yml ansible-docker-lab:/deploy.yml
docker cp ansible/inventory.ini ansible-docker-lab:/inventory.ini
```

Test it manually:

```bash
docker exec ansible-docker-lab ansible-playbook -i /inventory.ini /deploy.yml
docker ps
```
Open http://localhost:5002 and place a reservation.

(The inventory is copied over your old one, which has the same content. If your old Canteen pipeline still needs it, it keeps working because the host is the same.)

---

## STEP 6: Jenkins pipeline (Exp 4, 5, 6, 10)

Start Jenkins and give it Docker access (same as your lab):

```bash
docker start jenkins
docker start ansible-docker-lab
docker exec -u root jenkins chmod 666 /var/run/docker.sock
```

In Jenkins (http://localhost:9091):

1. **New Item** → name `BookNestPipeline` → **Pipeline** → OK
2. Definition: **Pipeline script from SCM**
3. SCM: **Git**, Repository URL: `https://github.com/<your-username>/BookNest.git`
4. Branch: `*/master`, Script Path: `Jenkinsfile`
5. Save → **Build Now**

Stages that run: Checkout → Build Docker Image → Run Tests → Deploy with Ansible.
Open **Console Output** and confirm `Finished: SUCCESS`.

---

## STEP 7: Verify and capture evidence

```bash
docker ps
docker volume ls
docker volume inspect booknest_data
docker exec booknest-app python -c "import sqlite3; c=sqlite3.connect('data/booknest.db'); print(c.execute('SELECT * FROM reservations').fetchall())"
```

Persistence check:

```bash
docker rm -f booknest-app
docker exec ansible-docker-lab ansible-playbook -i /inventory.ini /deploy.yml
```
Reload http://localhost:5002/reservations: your reservations are still there.

---

## Screenshots to take

1. App home page (:5002) and reservation success toast
2. `/reservations` page
3. GitHub repo, commit history, merged branch (`git log --graph`)
4. Jenkins pipeline stage view and Console Output (SUCCESS)
5. Pytest output (4 passed)
6. Ansible playbook output (`failed=0`)
7. `docker ps` and `docker volume ls`
8. SQLite query output

---

## Experiment mapping

| Exp | Covered by |
|-----|-----------|
| 1 | Step 2: git init, commit, remote |
| 2 | Step 2: push, fetch, pull |
| 3 | Step 3: branch and merge |
| 4 | Step 6: Jenkins job from Git |
| 5 | Jenkinsfile pipeline |
| 6 | Optional: GitHub webhook trigger (Poll SCM `* * * * *` in job config) |
| 7, 8 | Step 4: Dockerfile and build |
| 9 | Step 4/5: web app in a container |
| 10 | Pytest stage in Jenkinsfile |
| 11, 12 | Step 5: Ansible playbook managing the container |
