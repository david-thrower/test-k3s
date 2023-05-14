
## Create a main (control plane)
```
multipass launch -c 1 -m 1G -d 4G --mount /dev-k8s:/home/ubuntu/work -n k3s-main 22.04;
multipass exec k3s-main -- bash -c "curl -sfL https://get.k3s.io | sh -"
```

## Set up the nodes

### Create the VMs for the nodes
```
for f in 1 2; do
    multipass launch -c 2 -m 2G -d 10G -n k3s-node-$f 22.04
done
```

### Get the credentials for the nodes to join the main
```
K3_TOKEN=$(multipass exec k3s-main sudo cat /var/lib/rancher/k3s/server/node-token)
```

### Get the IP adddress for the main  
```
K3_IP=$(multipass info k3s-main | grep IPv4 | awk '{print $2}')
```

### Install the kubelets on the node VMs
```
for f in 1 2; do
    multipass exec k3s-node-$f -- bash -c "curl -sfL https://get.k3s.io | K3S_URL=\"https://$K3_IP:6443\" K3S_TOKEN=\"$K3_TOKEN\" sh -"
done
```

# Credits

- Obviously the K3S docs
- https://andreipope.github.io/tutorials/create-a-cluster-with-multipass-and-k3s.html
