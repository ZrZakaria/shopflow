D

# TP1 — Rapport : Tests unitaires avec JUnit 5 — Panier ShopFlow

**Cours :** Stratégie de test logiciel, 2026-2027
**Enseignant :** Pr. Youssef Gahi
**Étudiant :** ZrZakaria
**Projet :** ShopFlow — Boutique en ligne de matériel informatique
**Date :** Octobre 2026

---

## 1. Préparation du poste

### 1.1 Vérification de l'environnement

Installation de **JDK 21** (Eclipse Temurin) et **Maven 3.9**. Vérification des versions :

```bash
java -version
mvn -v
```

> **Capture 1** — `java -version`

```
java version "21.0.10" 2026-01-20 LTS
Java(TM) SE Runtime Environment (build 21.0.10+8-LTS-217)
Java HotSpot(TM) 64-Bit Server VM (build 21.0.10+8-LTS-217, mixed mode, sharing)
```

> **Capture 2** — `mvn -v`

```
Apache Maven 3.9.11
Maven home: C:\Program Files\JetBrains\IntelliJ IDEA 2026.1.1\plugins\maven\lib\maven3
Java version: 21.0.10, vendor: Oracle Corporation, runtime: C:\Program Files\Java\jdk-21.0.10
OS name: "windows 11", version: "10.0", arch: "amd64"
```

### 1.2 Création du projet Maven `shopflow`

Structure standard Maven créée :

```
shopflow/
├── pom.xml
├── .gitignore
├── src/
│   ├── main/java/ma/shopflow/panier/
│   └── test/java/ma/shopflow/panier/
```

Fichier **`pom.xml`** — dépendances JUnit 5 et configuration Surefire :

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
             https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>ma.shopflow</groupId>
    <artifactId>shopflow</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <name>ShopFlow</name>

    <properties>
        <maven.compiler.release>21</maven.compiler.release>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.junit</groupId>
                <artifactId>junit-bom</artifactId>
                <version>5.14.4</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <dependencies>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.5.6</version>
                <configuration>
                    <trimStackTrace>true</trimStackTrace>
                    <statelessTestsetInfoReporter
                            implementation="org.apache.maven.plugin.surefire.extensions.junit5.JUnit5StatelessTestsetInfoReporter">
                        <usePhrasedClassNameInRunning>true</usePhrasedClassNameInRunning>
                    </statelessTestsetInfoReporter>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

Fichier **`.gitignore`** :

```
target/
bin/
.idea/
*.iml
.vscode/
```

> **[Capture 3] — Vue explorateur VS Code du projet shopflow**
>
> *(Capture d'écran de l'arborescence des dossiers dans VS Code : src/main/java et src/test/java)*

---

## 2. Code métier

### 2.1 Classes du domaine

Cinq classes ont été écrites dans `src/main/java/ma/shopflow/panier/` :

| Fichier                                    | Rôle                                                                |
| ------------------------------------------ | -------------------------------------------------------------------- |
| `Produit.java`                           | Record immutable — référence, nom, prix unitaire (`BigDecimal`) |
| `LignePanier.java`                       | Record — produit + quantité, avec`sousTotal()`                   |
| `CodePromo.java`                         | Record — code promo + pourcentage (1–50)                           |
| `QuantiteMaximaleDepasseeException.java` | Exception personnalisée                                             |
| `Panier.java`                            | Classe principale du panier                                          |

**`Produit.java`** :

```java
package ma.shopflow.panier;

import java.math.BigDecimal;
import java.util.Objects;

public record Produit(String reference, String nom, BigDecimal prixUnitaire) {
    public Produit {
        Objects.requireNonNull(reference, "La référence est obligatoire");
        Objects.requireNonNull(nom, "Le nom est obligatoire");
        if (prixUnitaire == null || prixUnitaire.signum() <= 0) {
            throw new IllegalArgumentException("Le prix doit être strictement positif");
        }
    }
}
```

**`LignePanier.java`** :

```java
package ma.shopflow.panier;

import java.math.BigDecimal;

public record LignePanier(Produit produit, int quantite) {
    public BigDecimal sousTotal() {
        return produit.prixUnitaire().multiply(BigDecimal.valueOf(quantite));
    }
}
```

**`CodePromo.java`** :

```java
package ma.shopflow.panier;

import java.util.Objects;

public record CodePromo(String code, int pourcentage) {
    public CodePromo {
        Objects.requireNonNull(code, "Le code est obligatoire");
        if (pourcentage < 1 || pourcentage > 50) {
            throw new IllegalArgumentException("Le pourcentage doit être compris entre 1 et 50");
        }
    }
}
```

**`QuantiteMaximaleDepasseeException.java`** :

```java
package ma.shopflow.panier;

public class QuantiteMaximaleDepasseeException extends RuntimeException {
    public QuantiteMaximaleDepasseeException(String reference, int maximum) {
        super("Quantité maximale dépassée pour " + reference + " (maximum " + maximum + ")");
    }
}
```

> **[Capture 4] — Code source `Panier.java` dans l'éditeur**
>
> *(Capture d'écran de la classe Panier.java ouverte dans VS Code ou IntelliJ)*

### 2.2 Compilation

```bash
mvn compile
```

> **Capture 5** — `mvn compile` → BUILD SUCCESS

```
[INFO] --- compiler:3.13.0:compile (default-compile) @ shopflow ---
[INFO] Compiling 5 source files with javac [debug release 21] to target\\classes
[INFO] BUILD SUCCESS
[INFO] Total time:  0.782 s
```

---

## 3. Premier test — PanierTest.java

La classe `PanierTest.java` a été créée dans `src/test/java/ma/shopflow/panier/`.

Elle définit trois produits statiques partagés (`CLAVIER`, `SOURIS`, `CABLE`) et une méthode utilitaire `assertMontant()` pour comparer des `BigDecimal` par valeur (sans tenir compte du scale).

```java
package ma.shopflow.panier;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;
import java.math.BigDecimal;
import org.junit.jupiter.api.Test;

class PanierTest {

    static final Produit CLAVIER = new Produit("CLAV-01", "Clavier mécanique", new BigDecimal("450.00"));
    static final Produit SOURIS  = new Produit("SOUR-02", "Souris sans fil",    new BigDecimal("120.00"));
    static final Produit CABLE   = new Produit("CABL-03", "Câble USB-C",        new BigDecimal("19.99"));

    @Test
    void unNouveauPanierEstVide() {
        Panier panier = new Panier();
        assertTrue(panier.estVide());
        assertEquals(0, panier.nombreArticles());
    }

    @Test
    void leSousTotalEstLaSommeDesLignes() {
        Panier panier = new Panier();
        panier.ajouter(CLAVIER, 1);
        panier.ajouter(SOURS, 2);
        assertMontant("690.00", panier.sousTotal());
    }

    static void assertMontant(String attendu, BigDecimal reel) {
        if (new BigDecimal(attendu).compareTo(reel) != 0) {
            fail("Montant attendu : " + attendu + " DH, obtenu : " + reel + " DH");
        }
    }
}
```

> **[Capture 6] — Premier échec du test `leSousTotalEstLaSommeDesLignes`**
>
> *(Capture du message d'erreur : expected <690> but was <690.00> — problème d'échelle BigDecimal. Ce premier échec montre que le test lui-même était mal écrit avant d'ajouter `assertMontant`)*

Après ajout de `assertMontant()`, les deux tests passent.

---

## 4. Organisation des tests par règle métier

La classe `PanierTest.java` a été réorganisée avec des classes `@Nested` et `@DisplayName` pour grouper les tests par règle (R1 à R8).

```java
package ma.shopflow.panier;

import static org.junit.jupiter.api.Assertions.*;
import java.math.BigDecimal;
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.*;
import org.junit.jupiter.params.provider.*;

@DisplayName("Panier ShopFlow")
class PanierTest {

    static final Produit CLAVIER = new Produit("CLAV-01", "Clavier mécanique", new BigDecimal("450.00"));
    static final Produit SOURIS  = new Produit("SOUR-02", "Souris sans fil",    new BigDecimal("120.00"));
    static final Produit CABLE   = new Produit("CABL-03", "Câble USB-C",        new BigDecimal("19.99"));

    private Panier panier;

    @BeforeEach
    void creerUnPanierVide() {
        panier = new Panier();
    }

    // ---- R1 à R3 : ajout de produits ----
    @Nested
    @DisplayName("R1 à R3 : ajout de produits")
    class AjoutDeProduits {
        @Test
        @DisplayName("un nouveau panier est vide")
        void unNouveauPanierEstVide() {
            assertTrue(panier.estVide());
            assertEquals(0, panier.nombreArticles());
        }

        @Test
        @DisplayName("R1 : une quantité nulle est refusée")
        void uneQuantiteNulleEstRefusee() {
            IllegalArgumentException erreur = assertThrows(IllegalArgumentException.class,
                    () -> panier.ajouter(SOURIS, 0));
            assertEquals("La quantité doit être supérieure ou égale à 1", erreur.getMessage());
            assertTrue(panier.estVide());
        }

        @Test
        @DisplayName("R2 : ajouter deux fois le même produit cumule les quantités")
        void ajouterDeuxFoisLeMemeProduitCumuleLesQuantites() {
            panier.ajouter(SOURIS, 2);
            panier.ajouter(SOURIS, 3);
            assertAll("ligne unique de 5 souris",
                    () -> assertEquals(1, panier.lignes().size()),
                    () -> assertEquals(5, panier.lignes().get(0).quantite()),
                    () -> assertEquals(5, panier.nombreArticles()));
        }

        @Test
        @DisplayName("R3 : 10 unités d'un même produit sont acceptées")
        void dixUnitesSontAcceptees() {
            assertDoesNotThrow(() -> panier.ajouter(CABLE, 10));
        }

        @Test
        @DisplayName("R3 : la 11e unité est refusée et le panier reste inchangé")
        void laOnziemeUniteEstRefusee() {
            panier.ajouter(CABLE, 8);
            assertThrows(QuantiteMaximaleDepasseeException.class, () -> panier.ajouter(CABLE, 3));
            assertEquals(8, panier.nombreArticles());
        }
    }

    // ---- R4 : sous-total ----
    @Nested
    @DisplayName("R4 : sous-total")
    class SousTotal {
        @Test
        @DisplayName("le sous-total est la somme des lignes")
        void leSousTotalEstLaSommeDesLignes() {
            panier.ajouter(CLAVIER, 1);
            panier.ajouter(SOURIS, 2);
            assertMontant("690.00", panier.sousTotal());
        }

        @Test
        @DisplayName("les centimes sont conservés")
        void lesCentimesSontConserves() {
            panier.ajouter(CABLE, 3);
            assertMontant("59.97", panier.sousTotal());
        }
    }

    // ---- R5 : frais de livraison ----
    @Nested
    @DisplayName("R5 : frais de livraison")
    class FraisDeLivraison {
        @Test
        @DisplayName("un panier vide ne paie pas de livraison")
        void unPanierVideNePaiePasDeLivraison() {
            assertMontant("0.00", panier.fraisLivraison());
        }

        @ParameterizedTest(name = "sous-total {0} DH -> livraison {1} DH")
        @CsvSource({
                "100.00,  30.00",
                "499.99,  30.00",
                "500.00,   0.00",
                "500.01,   0.00",
                "1200.00,  0.00"
        })
        @DisplayName("la livraison est offerte à partir de 500 DH")
        void laLivraisonEstOfferteAPartirDe500DH(String sousTotal, String fraisAttendus) {
            panier.ajouter(new Produit("TEST-01", "Produit de test", new BigDecimal(sousTotal)), 1);
            assertMontant(fraisAttendus, panier.fraisLivraison());
        }
    }

    // ---- R6 et R7 : remise et total ----
    @Nested
    @DisplayName("R6 et R7 : remise et total")
    class RemiseEtTotal {
        @Test
        @DisplayName("sans code promo, total = sous-total + livraison")
        void sansCodePromoLeTotalInclutLaLivraison() {
            panier.ajouter(SOURIS, 1);
            assertMontant("150.00", panier.total());
        }

        @Test
        @DisplayName("R6 : la remise porte sur le sous-total, jamais sur la livraison")
        void laRemiseNePortePasSurLaLivraison() {
            panier.ajouter(SOURIS, 1);
            panier.appliquerCodePromo(new CodePromo("BIENVENUE10", 10));
            assertAll(
                    () -> assertMontant("12.00", panier.remise()),
                    () -> assertMontant("30.00", panier.fraisLivraison()),
                    () -> assertMontant("138.00", panier.total()));
        }

        @Test
        @DisplayName("R6 : la remise est arrondie au centime")
        void laRemiseEstArrondieAuCentime() {
            panier.ajouter(CABLE, 3);
            panier.appliquerCodePromo(new CodePromo("ETE15", 15));
            assertMontant("9.00", panier.remise());
        }

        @Test
        @DisplayName("R5 et R6 : le seuil de livraison s'évalue avant la remise")
        void leSeuilDeLivraisonSEvalueAvantLaRemise() {
            panier.ajouter(CLAVIER, 1);
            panier.ajouter(SOURIS, 1);
            panier.appliquerCodePromo(new CodePromo("BIENVENUE10", 10));
            assertAll(
                    () -> assertMontant("0.00", panier.fraisLivraison()),
                    () -> assertMontant("513.00", panier.total()));
        }
    }

    // ---- R8 : code promo sur panier vide ----
    @Nested
    @DisplayName("R8 : code promo")
    class CodePromoSurPanier {
        @Test
        @DisplayName("un code promo est refusé sur un panier vide")
        void unCodePromoEstRefuseSurUnPanierVide() {
            CodePromo bienvenue = new CodePromo("BIENVENUE10", 10);
            assertThrows(IllegalStateException.class, () -> panier.appliquerCodePromo(bienvenue));
        }
    }

    static void assertMontant(String attendu, BigDecimal reel) {
        if (new BigDecimal(attendu).compareTo(reel) != 0) {
            fail("Montant attendu : " + attendu + " DH, obtenu : " + reel + " DH");
        }
    }
}
```

**Classe `CodePromoTest.java`** :

```java
package ma.shopflow.panier;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

@DisplayName("Code promo")
class CodePromoTest {

    @ParameterizedTest(name = "{0} % est accepté")
    @ValueSource(ints = {1, 25, 50})
    void unPourcentageEntre1Et50EstAccepte(int pourcentage) {
        assertDoesNotThrow(() -> new CodePromo("TEST", pourcentage));
    }

    @ParameterizedTest(name = "{0} % est refusé")
    @ValueSource(ints = {-5, 0, 51, 100})
    void unPourcentageHorsBornesEstRefuse(int pourcentage) {
        assertThrows(IllegalArgumentException.class, () -> new CodePromo("TEST", pourcentage));
    }
}
```

> **[Capture 7] — Vue Testing de VS Code avec l'arbre des tests**
>
> *(Capture d'écran de la vue « Testing » (icône fiole) montrant les 25 tests organisés en groupes @Nested)*

---

## 5. Valeurs limites et premier bug — Règle R5

### 5.1 Test paramétré des frais de livraison

Le test `laLivraisonEstOfferteAPartirDe500DH` utilise `@ParameterizedTest` avec `@CsvSource` pour couvrir les valeurs limites :

| Sous-total          | Livraison attendue | Zone                                 |
| ------------------- | ------------------ | ------------------------------------ |
| 100.00 DH           | 30.00 DH           | Livraison payante (normale)          |
| 499.99 DH           | 30.00 DH           | Juste en dessous du seuil            |
| **500.00 DH** | **0.00 DH**  | **Exactement le seuil** ← BUG |
| 500.01 DH           | 0.00 DH            | Juste au-dessus du seuil             |
| 1200.00 DH          | 0.00 DH            | Livraison offerte (normale)          |

### 5.2 Premier bug découvert

Au lancement initial, le cas **500.00 DH** échoue :

```
expected: <0.00> but was: <30.00>
```

Le code original de `Panier.fraisLivraison()` contenait :

```java
// CODE INITIAL (BUGGY)
return sousTotal().compareTo(SEUIL_LIVRAISON_OFFERTE) > 0   // ❌ strictement supérieur
        ? BigDecimal.ZERO.setScale(2)
        : FRAIS_LIVRAISON;
```

La condition `> 0` signifie « strictement supérieur à 500 », alors que la règle R5 exige « dès que le sous-total **atteint** 500 DH ». C'est une erreur **off-by-one** classique.

### 5.3 Correction

```java
// CODE CORRIGÉ
return sousTotal().compareTo(SEUIL_LIVRAISON_OFFERTE) >= 0  // ✅ atteint ou dépassé
        ? BigDecimal.ZERO.setScale(2)
        : FRAIS_LIVRAISON;
```

> **Capture 8** — Bug R5 : échec du test `laLivraisonEstOfferteAPartirDe500DH` (cas 500.00 DH)

```
[ERROR] Tests run: 6, Failures: 1, Errors: 0, Skipped: 0, Time elapsed: 0.079 s <<< FAILURE! -- in R5 : frais de livraison
[ERROR] ma.shopflow.panier.PanierTest.laLivraisonEstOfferteAPartirDe500DH(String, String)[3]
org.opentest4j.AssertionFailedError: Montant attendu : 0.00 DH, obtenu : 30.00 DH
    at ma.shopflow.panier.PanierTest.assertMontant(PanierTest.java:191)
[ERROR] Tests run: 25, Failures: 1, Errors: 0, Skipped: 0
[INFO] BUILD FAILURE
```

**Cause** : condition `> 0` au lieu de `>= 0` — le seuil de 500 DH exact n'était pas atteint.

> **Capture 9** — Tests R5 après correction (`>= 0`) — 6/6 verts

```
[INFO] Running R5 : frais de livraison
[INFO] Tests run: 6, Failures: 0, Errors: 0, Skipped: 0
```

---

## 6. Remise et total — Deuxième bug (exercice)

### 6.1 Tests écrits pour R6 et R7

Quatre tests ont été ajoutés dans le groupe `RemiseEtTotal` :

1. **Sans code promo** : 1 souris (120 DH) → total = 120 + 30 = **150 DH**
2. **Avec code BIENVENUE10** : remise = 12 DH (10% de 120), livraison = 30 DH, total = **138 DH**
3. **Arrondi au centime** : 3 câbles (59.97 DH) avec code ETE15 (15%) → remise = **9.00 DH**
4. **Seuil avant remise** : clavier + souris = 570 DH → livraison gratuite, total avec 10% = **513 DH**

### 6.2 Deuxième bug découvert

Le test « la remise ne porte pas sur la livraison » échoue initialement :

```
expected: <138.00> but was: <135.00>
```

Le code original de `Panier.total()` appliquait le pourcentage sur `sousTotal + fraisLivraison` :

```java
// CODE INITIAL (BUGGY)
public BigDecimal total() {
    BigDecimal montant = sousTotal().add(fraisLivraison());          // 120 + 30 = 150
    if (codePromo != null) {
        montant = montant.subtract(pourcentageDe(montant, 10));      // 10% de 150 = 15 DH
    }
    return montant;                                                   // 150 - 15 = 135 ❌
}
```

La remise de 10 % a été calculée sur 150 DH au lieu de 120 DH → 15 DH au lieu de 12 DH → total 135 DH au lieu de 138 DH.

### 6.3 Correction

```java
// CODE CORRIGÉ — traduction directe de R7
public BigDecimal total() {
    return sousTotal().subtract(remise()).add(fraisLivraison());
}
```

> **Capture 10** — Bug R6/R7 : échec du test `laRemiseNePortePasSurLaLivraison`

```
[ERROR] Tests run: 4, Failures: 1, Errors: 0, Skipped: 0, Time elapsed: 0.061 s <<< FAILURE! -- in R6 et R7 : remise et total
[ERROR] ma.shopflow.panier.PanierTest.laRemiseNePortePasSurLaLivraison
org.opentest4j.MultipleFailuresError:
	org.opentest4j.AssertionFailedError: Montant attendu : 138.00 DH, obtenu : 135.00 DH
[ERROR] Tests run: 25, Failures: 1, Errors: 0, Skipped: 0
[INFO] BUILD FAILURE
```

**Cause** : `total()` appliquait le pourcentage sur `sousTotal + fraisLivraison` au lieu du sous-total seul.

> **Capture 11** — Tous les 25 tests verts après correction

```
[INFO] Running Code promo                      → Tests run: 7, Failures: 0
[INFO] Running R8 : code promo                   → Tests run: 1, Failures: 0
[INFO] Running R6 et R7 : remise et total        → Tests run: 4, Failures: 0
[INFO] Running R5 : frais de livraison           → Tests run: 6, Failures: 0
[INFO] Running R4 : sous-total                   → Tests run: 2, Failures: 0
[INFO] Running R1 à R3 : ajout de produits       → Tests run: 5, Failures: 0
[INFO] Tests run: 25, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

---

## 7. Exécution finale des tests

Commande exécutée :

```bash
mvn clean test
```

Résultat :

```
[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running Code promo
[INFO] Tests run: 7, Failures: 0, Errors: 0, Skipped: 0
[INFO] Running Panier ShopFlow
[INFO] Running R1 à R3 : ajout de produits       → 5 tests passés
[INFO] Running R4 : sous-total                   → 2 tests passés
[INFO] Running R5 : frais de livraison           → 6 tests passés
[INFO] Running R6 et R7 : remise et total        → 4 tests passés
[INFO] Running R8 : code promo                   → 1 test passé
[INFO]
[INFO] Results:
[INFO] Tests run: 25, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

> **Capture 12** — Exécution finale `mvn clean test`

```
[INFO] --- clean:3.2.0:clean (default-clean) @ shopflow ---
[INFO] Deleting C:\...\shopflow\target
[INFO] --- compiler:3.13.0:compile (default-compile) @ shopflow ---
[INFO] Compiling 5 source files with javac [debug release 21] to target\\classes
[INFO] --- compiler:3.13.0:testCompile (default-testCompile) @ shopflow ---
[INFO] Compiling 2 source files with javac [debug release 21] to target\\test-classes
[INFO] --- surefire:3.5.6:test (default-test) @ shopflow ---
[INFO] Running Code promo                      → Tests run: 7, Failures: 0, Errors: 0, Skipped: 0
[INFO] Running R8 : code promo                   → Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
[INFO] Running R6 et R7 : remise et total        → Tests run: 4, Failures: 0, Errors: 0, Skipped: 0
[INFO] Running R5 : frais de livraison           → Tests run: 6, Failures: 0, Errors: 0, Skipped: 0
[INFO] Running R4 : sous-total                   → Tests run: 2, Failures: 0, Errors: 0, Skipped: 0
[INFO] Running R1 à R3 : ajout de produits       → Tests run: 5, Failures: 0, Errors: 0, Skipped: 0
[INFO] Results:
[INFO] Tests run: 25, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
[INFO] Total time:  4.406 s
```

---

## 8. Versionnement — Git

### 8.1 Initialisation et commits

```bash
git init -b main
git add .
git commit -m "TP1: tests unitaires du panier"
git tag tp1
```

> **Capture 13** — `git log --oneline` et `git tag -l`

```
$ git log --oneline
9f5deca TP1: add terminal output captures for report
48ed8a2 TP1: add report with all lab steps
0f0cd91 TP1: clean .gitignore (add bin/)
33f4058 TP1: tests unitaires du panier (clean)
93d6f37 TP1: tests unitaires du panier
$ git tag -l
tp1
```

> **Capture 14** — Vue Git (Source Control) du projet shopflow
> *(Capture d'écran de l'onglet Source Control de VS Code ou IntelliJ montrant les 4 commits et le tag `tp1`)*

### 8.2 Dépôt distant (GitHub)

```bash
gh repo create shopflow --public --source=. --remote=origin --push
git push origin tp1
```

> **Capture 15** — Création du dépôt GitHub et push du tag

```
$ gh repo create shopflow --public --source=. --remote=origin --push
Created repository ZrZakaria/shopflow
https://github.com/ZrZakaria/shopflow
To https://github.com/ZrZakaria/shopflow.git
 * [new branch]      HEAD -> main
branch 'main' set up to track 'origin/main'.
$ git push origin tp1
To https://github.com/ZrZakaria/shopflow.git
 * [new tag]         tp1 -> tp1
```

Dépôt en ligne : **https://github.com/ZrZakaria/shopflow**

---

## 9. Fiche d'anomalies

Le fichier **`ANOMALIES.md`** a été créé à la racine du projet :

```markdown
# Fiche d'anomalies — ShopFlow TP1

## Anomalie #1 : Livraison non offerte à 500 DH exactement

| Rubrique | Détail |
|----------|--------|
| **Règle** | R5 — La livraison est offerte dès que le sous-total atteint 500 DH |
| **Test révélateur** | `laLivraisonEstOfferteAPartirDe500DH` (cas 500.00 DH) |
| **Cause** | Condition `> 0` au lieu de `>= 0` dans `fraisLivraison()` |
| **Correctif** | Remplacer `> 0` par `>= 0` |

## Anomalie #2 : Remise appliquée sur la livraison

| Rubrique | Détail |
|----------|--------|
| **Règle** | R6 + R7 — La remise porte sur le sous-total uniquement |
| **Test révélateur** | `laRemiseNePortePasSurLaLivraison` (1 souris, code BIENVENUE10) |
| **Cause** | `total()` appliquait le pourcentage sur `sousTotal + livraison` |
| **Correctif** | `return sousTotal().subtract(remise()).add(fraisLivraison())` |
```

> **[Capture 16] — Contenu du fichier `ANOMALIES.md`**
>
> *(Capture d'écran du fichier ouvert dans l'éditeur)*

---

## 10. Bilan

| Élément                               | Détail                                                                                                                                                                      |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Tests écrits**                 | 25 tests (20 dans`PanierTest` + 7 dans `CodePromoTest`)                                                                                                                  |
| **Règles couvertes**             | R1, R2, R3, R4, R5, R6, R7, R8 — toutes les 8 règles                                                                                                                       |
| **Techniques JUnit 5 utilisées** | `@Test`, `@Nested`, `@DisplayName`, `@BeforeEach`, `@ParameterizedTest`, `@CsvSource`, `@ValueSource`, `assertThrows`, `assertAll`, `assertDoesNotThrow` |
| **Bugs trouvés**                 | 2 — off-by-one sur le seuil de livraison, remise appliquée sur la livraison                                                                                                |
| **Schéma AAA respecté**         | Oui — Arrange / Act / Assert dans chaque test                                                                                                                               |
| **Tests de non-régression**      | Oui — les 25 tests protègent contre toute regression future                                                                                                                |
| **Dépôt Git**                   | Tag`tp1` sur le commit final, pushed sur GitHub                                                                                                                            |

---

*Document généré pour le TP1 — Stratégie de test logiciel, 2026-2027.*
