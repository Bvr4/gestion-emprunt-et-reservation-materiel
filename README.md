# Gestion Emprunt et Réservation de Matériel (GERM)
Ce projet a pour but de permettre la gestion de l’emprunt et de la réservation de matériel au sein d’une coopérative d’outils.

## Fonctionnalités
Il existe deux type d'utilisateurs: les usagers et les modérateurs, ayant accès à des fonctionnalités différentes.  
Tous peuvent réserver et emprunter du matériel.  
Les matériels appartiennent à une catégorie, et sont disponibles à un emplacement. Ils peuvent être empruntables, ou non. Ils ont un identifiant unique, dont le préfixe est défini par la catégorie à laquelle ils appartiennent. On peut laisser des commentaires sur la fiche du matériel, pour assurer le suivi et la communication entre les utilisateurs.  
Les modérateurs peuvent créer, modifier, supprimer du matériel, des espaces, des catégories.  
Une fiche matériel permet d'accéder aux informations du matériel, de procéder à sa réservation et son emprunt, de voir les réservations en cours, passées et futures. 

## Stack technique
Django pour le back-end, htmx et picocss pour le front-end.
     
Projet en cours de développement.
