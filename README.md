# Kubernetes Connectivity Checker

Kubernetes Connectivity Checker was created for .. checking http(s) connnectivity in Kubernetes environments with several admin network policies, network policies, and baseline admin network policies defined.

Some parameters of checks such as target url, check interval, accepted status code, proxy can be configured.

The check result is made available in a status page /status on port 8080 in form of simple OK, NOK message, while more information can be found in the STDOUT log.

This program should work with 2 other programs (which are outside of this repo):

- provisioning of k8s connectivity checkers on a Kubernetes cluster
- visualization dashboard of k8s connectivity checker results

## Build

Code can be used direcly or inside a Docker container. To create a Docker image, run:

```bash
docker build -t k8s-connectivity-checker .
```

## Configuration

Program is configured using environment variables:

|Variable|Required|Description|Default|
|--------|--------|-----------|-------|
|TARGET_URL|yes|HTTP(s) endpoint to check|-|
|CHECK_INTERVAL|no|Interval between checks|60s|
|ACCEPTED_STATUS_CODES|no|When defined, check is marked as successful only if returned http status code is included in this parameter|200|
|HTTP_PROXY|no|Proxy address to use for http checks|-|
|HTTPS_PROXY|no|Proxy address to use for https checks|-|

## Usage

While the program was created with the specific need of checking K8s connectivity, it can be used outside of the Kubernetes ecosystem.

### Direct usage

Program can be executed directly using Python virtual environment.

#### Environment preparation

When running the program directly using Python, a virtual environment has to be created, and dependencies installed:

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

#### Python execution

Supply parameters using environment variables, e.g.:

```bash
TARGET_URL=https://example.com python3 app.py
```

### Docker container

#### Build image

For instructions on how to build checker docker image see [Build](#build)

#### Docker container execution

```bash
docker run -e TARGET_URL=https://example.com k8s-connectivity-checker
```

#### Build image and push to registry

For instructions on how to build checker docker image see [Build](#build)

Image has to be available for the Kubernetes cluster => push to a OCI registry:

```bash
docker push <registry_url>/k8s-connectivity-checker:latest
```

### Kubernetes cluster

Create a deployment:

```bash
kubectl create deployment listener --image="<registry-url>/k8s-connectivity-checker" -n "<namespace>"
kubectl patch deployment listener -n "<namespace>" -p "{\"spec\": {\"template\": {\"spec\": {\"imagePullSecrets\": [{\"name\": \"<secret-with-docker-credentials>\"}], \"containers\": [{\"name\": \"k8s-connectivity-checker\", \"env\": [{\"name\": \"TARGET_URL\", \"value\": \"http://listener:8080/status\"}]}]}}}}"
```

## TODO

- supply k8s manifests
- provisioning / visualisation dashboard
