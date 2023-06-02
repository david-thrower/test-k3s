
# Manually create a k3s Kubernetes cluster on cloud VMs

## Create the control plane nodes

### Create 1 VM like this (control plane)
- Name: "test-k3s-ctrl-0001-0001", default configuration with https and ssh network access
- Note its puplic IP address (or DNS name). Replace **all** occurrences of "**[IP address]**" with this IP (not the IP of the machine / VM which you are entering this on).
  - Install the control plane:
    - SSH in and run this: `curl -sfL https://get.k3s.io | K3S_TOKEN=SECRET sh -s - server --cluster-init --service-cidr 10.10.10.0/24`
    - Run:
    ```
    sudo chmod 777 /etc/rancher/k3s/k3s.yaml; export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
    echo "export KUBECONFIG=/etc/rancher/k3s/k3s.yaml" >> ~/.bashrc
    echo "export KUBECONFIG=/etc/rancher/k3s/k3s.yaml" >> ~/.profile
    ```
  - Get the credentials to join the cluster: Run: `sudo cat /var/lib/rancher/k3s/server/node-token`. Get the output of this and temporarily paste it into a text editor on your desktop. Replace **each** occurrence of **[Token]** throughout these instructions with this credential. Treat this as you would any password or ssh key. I do not recommend saving this to a disk though. Once the steps downstream are completed, delete it.  
  - Also write down the public IP address of this VM (from the cloud provider's web console)

## Create another VM as Name: "test-k3s-ctrl-0011-0002" (Second control plane)

- SSH into this one and run "curl -sfL https://get.k3s.io | K3S_TOKEN=**[Token]**" sh -s - server --server https://**[IP address]**:6443 --service-cidr 10.10.10.0/24" [**NOT this VM's IP address, the one from test-k3s-ctrl-0001-0001**)]
- Repeat these commands on this machine:
```
sudo chmod 777 /etc/rancher/k3s/k3s.yaml; export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
echo "export KUBECONFIG=/etc/rancher/k3s/k3s.yaml" >> ~/.bashrc
echo "export KUBECONFIG=/etc/rancher/k3s/k3s.yaml" >> ~/.profile
```

### Optionally create additional control plane nodes (3 at a minimum is recommended.):

- Test that what we did thus far was successful from one of these ssh connections: `kubectl get nodes` ... the result ought to look like **this**.
"""
NAME                 STATUS   ROLES                           AGE   VERSION
k3s-ctrl-0002-0001   Ready    **control-plane,etcd,master**   30m   v1.26.4+k3s1
k3s-ctrl-0002-0002   Ready    **control-plane,etcd,master**   1m   v1.26.4+k3s1
...
"""

- Close all but one of these SSH connections. Keep one open. You will need it later.

## We have a highly availible control plane set up. Now we just need the agents (nodes / kubelets):


## Create the agents (nodes / kubelets):

### Create 3 VMs like:

- Name: k3s-node-0001-0001
- Name: k3s-node-0001-0002
- Name: k3s-node-0001-0003

In each: SSH in and run the command:

- "curl -sfL https://get.k3s.io | K3S_URL="https://**[IP address]**:6443" K3S_TOKEN="**[Token]**" sh -"

## Add longhorn block storage for ReadWriteMany block storage and storage backup:

- Check the requirements. The Ubuntu machines have them met already. If any turn out to not be met, find the shortcut to add it with  `kubectl apply -f ...`, rather than installing them on the host OS.

```
kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.4.2/deploy/longhorn.yaml
```

## Install an app:

On a while logged into a control plane node on the cluster, run `nano deployment.yaml` and paste in  the contents of deployment.yaml (or clone this repo and open the file). In the file deployment.yaml: Amend this `test-app-deployment.test-app.[REPLACE-WITH-HOST-IP].sslip.io` to be "test-app-deployment.test-app.**[IP address]**.sslip.io". Then apply the resources: `kubectl apply -f deployment.yaml`.


## Add TLS and DNS

`kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.7.0/cert-manager.yaml`

issuer.yaml
```
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
  namespace: test-app
spec:
  acme:
    # You must replace this email address with your own.
    # Let's Encrypt will use this to contact you about expiring
    # certificates, and issues related to your account.
    email: david@cerebros.one
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    privateKeySecretRef:
      # Secret resource that will be used to store the account's private key.
      name: example-issuer-account-key
    # Add a single challenge solver, HTTP01 using nginx
    solvers:
    - http01:
        ingress:
          class: nginx

```

- Create a file: `cert.yaml` with the content below.
- Don't forget to replace **[IP address]** with the one from before.  
- `run kubectl apply -f cert.yaml`
```
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: test-app-cert
  namespace: test-app
spec:
  dnsNames:
  - 'test-app-deployment.test-app.[IP address].sslip.io'
  issuerRef:
    kind: ClusterIssuer
    name: letsencrypt-staging
  secretName: test-app-cert-pvc
```

- Create a file: `patch.yaml` with the content below
- Run the command `kubectl patch ingressroute test-app-ingress -n test-app --type=json --patch-file patch.yaml`

```
- op: replace
  path: /spec/entryPoints
  value:
    - websecure
- op: add
  path: /spec/tls
  value:
    secretName: test-app-cert-pvc
```



- Create the file: `redirect.yaml`
- - Don't forget to replace **[IP address]** with the one from before.
- rune the command: `kubectl apply -f redirect.yaml`
```
apiVersion: traefik.containo.us/v1alpha1
kind: Middleware
metadata:
  name: redirect-permanent
  namespace: test-app
spec:
  redirectScheme:
    permanent: true
    scheme: https
---
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: test-app-http-redir
  namespace: test-app
spec:
  entryPoints:
  - web
  routes:
  - kind: Rule
    match: Host("test-app-deployment.test-app.[IP address].sslip.io")
    services:
    - name: api@internal
      kind: TraefikService
    middlewares:
    - name: redirect-permanent
```

## Add authentication (Make sure this step is always applied AFTER the https redirect):
- Run the command `sudo apt install -y apache2-utils`
- Run the command: `htpasswd -c users you@youremail.com`
- Create a password as it will direct you to do.
- Add any additional users: `htpasswd users them@theiremail.com`
- Create a default password for them also.
- Run the command `kubectl create secret generic test-app-users --from-file=users -n test-app`

- Run `nano auth.yaml`
- Paste this in:
```
apiVersion: traefik.containo.us/v1alpha1
kind: Middleware
metadata:
  name: test-app-auth
  namespace: test-app
spec:
  basicAuth:
    secret: test-app-users
```
- Run the command: `kubectl apply -f auth.yaml`

Amend the last section of the deployment.yaml to show:
```
apiVersion: traefik.containo.us/v1alpha1
kind: IngressRoute
metadata:
  name: test-app-ingress
  namespace: test-app
spec:
  entryPoints:
  - websecure
  routes:
  - kind: Rule
    match: Host("test-app-deployment.test-app.[REPLACE-WITH-HOST-IP].sslip.io")
    middlewares:
    - name: test-app-auth
      namespace: test-app
    services:
    - name: test-app-service-cip
      port: 5000
  tls:
    secretName: test-app-cert-pvc
```

###

## Now to fortify security, we need a service mesh. **You may wan to skip this step if you plan to install a manifest that comes packaged with its own service mesh**

1. SSH into any of the **control plane** nodes (the first ones we set up)
2. Now run these commands. Rubber stamp anything it asks you "Are you sure..."
  1. `sudo snap install helm --classic`
  2. `helm repo add traefik https://traefik.github.io/charts`
  3. `helm repo update`
  4. `helm install traefik-mesh traefik/traefik-mesh`



## Now we have a production ready Kubernetes cluster ready to go.

# Credits

- Obviously the K3S docs
- https://andreipope.github.io/tutorials/create-a-cluster-with-multipass-and-k3s.html
