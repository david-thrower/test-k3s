### Old tls attempt: (probably delete)
## Now setup cert-manager to manage tls certificates for services



### First install cert-manager:

`kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.7.0/cert-manager.yaml`



clusterissuer.yaml
```
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    # You must replace this email address with your own.
    # Let's Encrypt will use this to contact you about expiring
    # certificates, and issues related to your account.
    email: user@example.com
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

app-cert.yaml
```
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: dashboard
spec:
  dnsNames:
  - 'dashboard.traefik.10.68.0.70.sslip.io'
  issuerRef:
    kind: ClusterIssuer
    name: selfsigned
  secretName: dashboard-crt
```



### Next configure cert-manager
- Start with the staging config below,
- After testing it, run the production config at the end.
- The production config will get you booted out of the system / detected as abuse if you make too many of certain types of errors. Start with the staging as seen below!

### Staging config:

- Replace the email with the administrator's email
- Save this file as "cert-manager-config.yaml"
- Apply it as `kubectl apply -f cert-manager-config.yaml`

```
# apiVersion: v1
# kind: Namespace
# metadata:
#   name: letsencrypt-staging
# ---
apiVersion: cert-manager.io/v1alpha2
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
  namespace: letsencrypt-staging
spec:
  acme:
    # The ACME server URL
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    # Email address used for ACME registration
    email: <your_email>@example.com
    # Name of a secret used to store the ACME account private key
    privateKeySecretRef:
      name: letsencrypt-staging
    # Enable the HTTP-01 challenge provider
    solvers:
    - http01:
        ingress:
          class: traefik
```
Example: Add to deployment YAMLs:

###  Only do the next step when you are deploying an application:
- Replace secretName with a suitable name (unique for each service)
- Replace commonName and dnsNames with the domain name you want.
- Append the deployment yaml for your app with the result of this:

```
---
apiVersion: cert-manager.io/v1alpha2
kind: Certificate
metadata:
  name: k3s-carpie-net
  namespace: default
spec:
  secretName: foo-com-tls
  issuerRef:
    name: letsencrypt-staging
    kind: ClusterIssuer
  commonName: foo.com
  dnsNames:
  - foo.com
```
