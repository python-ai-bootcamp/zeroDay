import subprocess
def startDockerContainer():
    print("stopping all conainers with name='task_runner'")
    subprocess.call(["docker", "container", "stop", "task_runner"])
    print("removing all stopped containers")
    subprocess.call(["docker", "container", "prune", "-f"])
    print("force killing container named 'task_runner' if from some reason he remained alive")
    subprocess.call(["docker", "container", "rm", "--force", "task_runner"])
    print("starting container named task_runner from image alpine:python_task_runner in daemon mode")
    subprocess.call(["docker", "run", "-t", "-d", "--name", "task_runner", "alpine:python_task_runner"])
