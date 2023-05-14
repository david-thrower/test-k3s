
# Manually create a k3s Kubernetes cluster on cloud VMs

## Create the control plane nodes

### Create 1 VM like this (control plane)

- Name: "test-k3s-ctrl-1-0001", default configuration with https and ssh network access
  - Install the control plane:
    - SSH in and run this: `curl -sfL https://get.k3s.io | K3S_TOKEN=SECRET sh -s - server --cluster-init --service-cidr 10.10.10.0/24`
    - Run `sudo chmod 777 /etc/rancher/k3s/k3s.yaml; export KUBECONFIG=/etc/rancher/k3s/k3s.yaml`
    - Run `echo "export KUBECONFIG=/etc/rancher/k3s/k3s.yaml" >> ~/.bashrc` and `echo "export KUBECONFIG=/etc/rancher/k3s/k3s.yaml" >> ~/.profile`
  - Get the credentials to join the cluster: Run: `sudo cat /var/lib/rancher/k3s/server/node-token`. Get the output of this and temporarily paste it into a text editor on your desktop. I do not recommend saving this to a disk though. Once the steps downstream are completed, delete it  
  - Also write down the public IP address of this VM (from the cloud provider's web console)

## Create another VM as Name: "test-k3s-ctrl-1-0002" (Second control plane)

- SSH h in to this one and run `curl -sfL https://get.k3s.io | K3S_TOKEN="[credentials from last step]" sh -s - server --server https://[ip-address-of test-k3s-ctrl-1-**0001**, (**NOT this VM**)]:6443 --service-cidr 10.10.10.0/24`
- Repeat these:
```
sudo chmod 777 /etc/rancher/k3s/k3s.yaml; export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
echo "export KUBECONFIG=/etc/rancher/k3s/k3s.yaml" >> ~/.bashrc
echo "export KUBECONFIG=/etc/rancher/k3s/k3s.yaml" >> ~/.profile

```

### Optionally create additional control plane nodes:

- Test that what we did thus far was successful: `kubectl get nodes` ... the result ought to look like **this**.
"""
NAME                 STATUS   ROLES                           AGE   VERSION
k3s-ctrl-0002-0001   Ready    **control-plane,etcd,master**   30m   v1.26.4+k3s1
k3s-ctrl-0002-0002   Ready    **control-plane,etcd,master**   1m   v1.26.4+k3s1
"""

### We have a highly availible control plane set up. Now we just need the agents (nodes / kubelets):


## Create the agents (nodes / kubelets):

### Create 3 VMs like:

- Name: k3s-node-0001-0001
- Name: k3s-node-0001-0002
- Name: k3s-node-0001-0003

In each: SSH in and run:

- `curl -sfL https://get.k3s.io | K3S_URL="https://[control plane ip]:6443" K3S_TOKEN="[token]" sh -`

## Now to fortify security, we need a service mesh. **You may wan to skip this step if you plan to install a manifest that comes packaged with its own service mesh (for example Kubeflow)**

1. SSH into any of the **control plane** nodes (the first ones we set up)
2. Now run these commands. Rubber stamp anything it asks you "Are youy sure..."
  1. `sudo snap install helm --classic`
  2. `helm repo add traefik https://traefik.github.io/charts`
  3. `helm repo update`
  4. `helm install traefik-mesh traefik/traefik-mesh`



## Now we have a production ready Kubernetes cluster ready to go.

# Credits

- Obviously the K3S docs
- https://andreipope.github.io/tutorials/create-a-cluster-with-multipass-and-k3s.html
