Django website setup
=====================

You can start with the provided pyproject.toml or create your own using:

`poetry init`

Then run:

`poetry lock`

`poetry install`

`poetry run django-admin startproject mywebsite`

`mv mywebsite django_website`

`cd django_website`

`poetry run python manage.py startapp myapp`

Add items to INSTALLED_APPS in file mywebsite/setting.py:

    INSTALLED_APPS = [
        ...
        'rest_framework',
        'myapp.apps.MyappConfig',
    ]

Add to the beggining of file mywebsite/setting.py:

    import os

Edit the appropriate area in file mywebsite/setting.py:

    DEBUG = os.environ.get('DJANGO_DEBUG') == 'TRUE'

Edit the appropriate area in file mywebsite/setting.py:

    STATIC_URL = "static/"
    STATIC_ROOT = os.path.join(BASE_DIR, "static")

Edit the appropriate area in file mywebsite/setting.py:

    if os.environ.get("PGDATABASE") is not None:
        DATABASES = {
            'default': {
            'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get('PGDATABASE'),
                'USER': os.environ.get('PGDATAUSER'),
                'PASSWORD': os.environ.get('PGPASSWORD'),
                'HOST': os.environ.get('PGHOST'),
            }
        }
    elif os.environ.get("MONGODATABASE") is not None:
        DATABASES = {
                'default': {
                    'ENGINE': 'djongo',
                    'NAME': os.environ.get('MONGODATABASE'),
                    'USER': os.environ.get('MONGODATAUSER'),
                    'PASSWORD': os.environ.get('MONGOPASSWORD'),
                    'HOST': os.environ.get('MONGOHOST'),
                    'ENFORCE_SCHEMA': False,
                }
        }
    else:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

Add to the end of file mywebsite/setting.py:

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework.authentication.BasicAuthentication',
            'rest_framework.authentication.SessionAuthentication',
        ]
    }

Edit the appropriate area in file mywebsite/setting.py:

    ALLOWED_HOSTS = ['*']

Note: the ALLOWED_HOSTS must be fixed later to the proper domain of website instead of * (it is a security risk to leave it like that).

Edit file mywebsite/urls.py:

    from django.contrib import admin
    from django.urls import path, include

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('', include('myapp.urls'))
    ]


Edit files (create if does not exist) with the provided content:

    mywebsite/myapp/urls.py
    mywebsite/myapp/models.py
    mywebsite/myapp/views.py

`poetry run python manage.py makemigrations`

`poetry run python manage.py migrate`

`poetry run python manage.py createsuperuser`

`poetry run python manage.py runserver`

`curl -u username:password http://127.0.0.1:8000/`


Deploy Django on Kubernetes
============================
The first step is download and install Docker, kubectl and helm.

And then have kubectl properly configured to access your cluster on the cloud. e.g.:
* https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl
* https://docs.aws.amazon.com/eks/latest/userguide/create-kubeconfig.html

Alternatively, you can start a cluster on your computer using minikube. In this case, run `minikube tunnel` to allow access to LoadBalancer services.

Now to configure Kubernetes to run Django on Nginx, first build the Docker image using the provided Dockerfile:

`docker build . -t django_app`

if you a name other than "django_app" in the command above, then update the line "image: django_app" in django_conf.yaml with the chosen name.

The image should be available on the Docker registry for kubernetes to pull, or as an alternative, you can enter the minikube Docker context by running

`eval $(minikube -p minikube docker-env)`

and build then image there

`docker build . -t django_app`

You can now go the section for database that you wish to use to deploy your Django website.

Deploy using SQLite
========================
If you want to use SQLite for a first simple test (database is an ephemeral disk!), edit file django_conf.yaml and remove the following lines:

    env:
      - name: PGHOST
        valueFrom:
          secretKeyRef:
            name: pg-django-conf
            key: host
            optional: false
      - name: PGDATABASE
        valueFrom:
          secretKeyRef:
            name: pg-django-conf
            key: database
            optional: false
      - name: PGUSER
        valueFrom:
          secretKeyRef:
            name: pg-django-conf
            key: username
            optional: false
      - name: PGPASSWORD
        valueFrom:
          secretKeyRef:
            name: pg-django-conf
            key: password
            optional: false
      - name: MONGOHOST
        valueFrom:
          secretKeyRef:
            name: mongo-django-conf
            key: host
            optional: false
      - name: MONGODATABASE
        valueFrom:
          secretKeyRef:
            name: mongo-django-conf
            key: database
            optional: false
      - name: MONGOUSER
        valueFrom:
          secretKeyRef:
            name: mongo-django-conf
            key: username
            optional: false
      - name: MONGOPASSWORD
        valueFrom:
          secretKeyRef:
            name: mongo-django-conf
            key: password
            optional: false

And run:

`kubectl apply -f django_conf.yaml`

Deploy using PostgreSQL
========================

Edit file django_conf.yaml and remove the following lines refering to MongoDB configuration:

  - name: MONGOHOST
    valueFrom:
      secretKeyRef:
        name: mongo-django-conf
        key: host
        optional: false
  - name: MONGODATABASE
    valueFrom:
      secretKeyRef:
        name: mongo-django-conf
        key: database
        optional: false
  - name: MONGOUSER
    valueFrom:
      secretKeyRef:
        name: mongo-django-conf
        key: username
        optional: false
  - name: MONGOPASSWORD
    valueFrom:
      secretKeyRef:
        name: mongo-django-conf
        key: password
        optional: false

Edit the username and password at postgres_helm_conf.yaml and django_postgres_conf.yaml

Then install postgres on Kubernetes using helm:

`helm repo add bitnami https://charts.bitnami.com/bitnami`
`helm repo update`
`helm install postgresql -f postgresql_helm_conf.yaml bitnami/postgresql`

And run:

`kubectl apply -f django_postgresql_conf.yaml`
`kubectl apply -f django_conf.yaml`

Check the IP address of the website with

`kubectl get services`

You can optinally setup the pgAdmin webserver, first edit the email login and initial password at file pgadmin_conf.yaml

  - name: PGADMIN_DEFAULT_EMAIL
    value: user@somedomain.com
  - name: PGADMIN_DEFAULT_PASSWORD
    value: choose_the_initial_pgadmin_password

and then run

`kubectl apply -f pgadmin_conf.yaml`

Check the IP address of the website with

`kubectl get services`

Login to the pgAdmin website and change your password.

Deploy using MongoDB
========================

Edit file django_conf.yaml and remove the following lines refering to PostgreSQL configuration:

  - name: PGHOST
    valueFrom:
      secretKeyRef:
        name: pg-django-conf
        key: host
        optional: false
  - name: PGDATABASE
    valueFrom:
      secretKeyRef:
        name: pg-django-conf
        key: database
        optional: false
  - name: PGUSER
    valueFrom:
      secretKeyRef:
        name: pg-django-conf
        key: username
        optional: false
  - name: PGPASSWORD
    valueFrom:
      secretKeyRef:
        name: pg-django-conf
        key: password
        optional: false

Edit the username and password at mongo_helm_conf.yaml and django_mongo_conf.yaml

Then install mongo on Kubernetes using helm:

`helm repo add bitnami https://charts.bitnami.com/bitnami`
`helm repo update`
`helm install mongodb -f mongodb_helm_conf.yaml bitnami/mongodb`

And run:

`kubectl apply -f django_mongodb_conf.yaml`
`kubectl apply -f django_conf.yaml`

Check the IP address of the website with

`kubectl get services`


Multiple websites on a single IP
==================================

We can host multiple website using a single external IP address if own a domain name for each of them. The first step is to instead a Kubernetes Ingress Controller, see https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/

Note: GCP GKE already comes with a Ingress Controller pre-configured and in case of minikube, you can enable the Ingress Controller by running `minikube addons enable ingress`.

After that, change the service from `LoadBalancer` to `ClusterIP`:


    apiVersion: v1
    kind: Service
    metadata:
      name: django-service
    spec:
      type: ClusterIP
      selector:
        app: django
      ports:
      - name: http
        protocol: TCP
        port: 80

And create the ingress policy:

    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: ingress-app
    spec:
      rules:
        - host: your-subdomain.your-domain.com # change to your domain here
          http:
            paths:
              - path: /
                pathType: Prefix
                backend:
                  service:
                    name: django-service
                    port:
                      number: 80

After that, you can obtain the IP address of the website by running `kubectl get ingress` and you can your (sub)domain DNS record to that IP (for a simple test, you can force your computer DNS resolver to point to that IP address by editing the /etc/hosts in your computer).

Note that if you are using GKE, you need to add an annotation to your Ingress:

    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: ingress-app
      annotations:
        kubernetes.io/ingress.class: nginx
    spec:
    ...

You can add more websites by deploying then, creating additional `ClusterIP` services and adding rules to the ingress policy, e.g.:

    apiVersion: v1
    kind: Service
    metadata:
      name: another-django-service
    spec:
      type: ClusterIP
      selector:
        app: another-django-app
      ports:
      - name: http
        protocol: TCP
        port: 80
    ---
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: ingress-app
    spec:
      rules:
        - host: your-subdomain.your-domain.com # change to your domain here
          http:
            paths:
              - path: /
                pathType: Prefix
                backend:
                  service:
                    name: django-service
                    port:
                      number: 80
        - host: another-subdomain.another-domain.com # change to your domain here
          http:
            paths:
              - path: /
                pathType: Prefix
                backend:
                  service:
                    name: another-django-service
                    port:
                      number: 80

Obtain free SSL certificates and serve a HTTPS server
=======================================================

After your DNS record has been sucessfully setuped and the HTTP website is running correctly, you can install obtain free Let's Encrypt SSL certificates for your website, first install a cert-manager addon to your cluster using helm:

`helm install cert-manager jetstack/cert-manager --namespace cert-manager --create-namespace --set installCRDs=true`

Then you can

    apiVersion: cert-manager.io/v1
    kind: ClusterIssuer
    metadata:
      name: letsencrypt-prod
    spec:
      acme:
        server: https://acme-v02.api.letsencrypt.org/directory
        email: m@marcoinacio.com
        privateKeySecretRef:
          name: letsencrypt-prod
        solvers:
        - http01:
            ingress:
              name: ingress-app


An then add the cert-manager.io annotation plus the tls spec to your ingress policy:

    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      name: ingress-app
      annotations:
        cert-manager.io/cluster-issuer: letsencrypt-prod
    spec:
      tls:
      - hosts:
        - covid.marcoinacio.com
        secretName: covid-app-tls
      rules:
        - host: covid.marcoinacio.com
          http:
            paths:
              - path: /
                pathType: Prefix
                backend:
                  service:
                    name: covid-app-service
                    port:
                      number: 80

From then on, cert-manager should be able to automatically obtain and renew your SSL certificates. You can check the status of your certificate by running:

`kubectl get certificate`

It may take a few minutes for the validation to happen (add an extra if you changed the DNS record of your domain recently). You can get more details of the status and throubleshoot by running:

`kubectl describe clusterissuers`

`kubectl describe certificaterequests`
