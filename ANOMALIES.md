# Fiche d'anomalies — ShopFlow TP1

## Anomalie #1 : Livraison non offerte à 500 DH exactement

| Rubrique | Détail |
|----------|--------|
| **Règle** | R5 — La livraison est offerte dès que le sous-total **atteint** 500 DH |
| **Test révélateur** | `laLivraisonEstOfferteAPartirDe500DH` (cas 500.00 DH) |
| **Cause** | La condition utilisait `> 0` au lieu de `>= 0` : `sousTotal().compareTo(SEUIL_LIVRAISON_OFFERTE) > 0`. Le seuil était donc dépassé (strictement supérieur) au lieu d'être atteint. |
| **Correctif** | Remplacer `> 0` par `>= 0` dans `Panier.fraisLivraison()` (ligne 78) |

## Anomalie #2 : Remise appliquée sur la livraison

| Rubrique | Détail |
|----------|--------|
| **Règle** | R6 + R7 — La remise porte sur le **sous-total uniquement**, jamais sur la livraison. Total = sous-total − remise + livraison |
| **Test révélateur** | `laRemiseNePortePasSurLaLivraison` (1 souris à 120 DH, code BIENVENUE10) |
| **Cause** | La méthode `total()` calculait `sousTotal + fraisLivraison`, puis appliquait le pourcentage sur ce montant total. La remise était donc aussi déduite des frais de livraison (10 % de 150 DH = 15 DH au lieu de 10 % de 120 DH = 12 DH). |
| **Correctif** | Remplacer `total()` par : `return sousTotal().subtract(remise()).add(fraisLivraison());` |
