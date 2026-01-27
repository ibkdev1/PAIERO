# PAIERO - Guide de Démarrage Rapide
## Pour les Nouveaux Utilisateurs

---

## 🚀 Installation Rapide

### Si vous avez reçu PAIERO.app (macOS) ou PAIERO.exe (Windows):

1. **Double-cliquez sur l'application**
   - macOS: Si vous voyez un avertissement de sécurité, faites clic droit > Ouvrir

2. **Connexion par défaut:**
   - Identifiant: `admin`
   - Mot de passe: `admin`

3. **⚠️ Important:** Changez votre mot de passe immédiatement!

### Si vous avez reçu le dossier PAIERO complet:

```bash
cd PAIERO
pip install -r requirements.txt
python3 main.py
```

---

## 👤 Première Connexion

1. Lancez PAIERO
2. Entrez vos identifiants de connexion
3. L'écran principal s'affiche avec le tableau de bord

---

## 🎯 Fonctionnalités Principales

### 1️⃣ Tableau de Bord
**Ce que vous voyez:**
- Nombre total d'employés actifs
- Montant net à payer du mois
- Nombre de prêts actifs
- Dernière période de paie traitée

**Navigation:** Utilisez la barre latérale gauche pour accéder aux différents modules.

---

### 2️⃣ Gestion des Employés

**Accès:** Cliquez sur **👥 Employés** dans le menu

**Actions disponibles:**
- ✅ **Consulter** la liste des employés
- ✅ **Rechercher** par nom, ID ou poste
- ✅ **Ajouter** un nouvel employé (si autorisé)
- ✅ **Modifier** les informations (si autorisé)
- ✅ **Supprimer** un employé (si autorisé)

**Pour ajouter un employé:**
1. Cliquez sur **+ Ajouter Employé**
2. Remplissez le formulaire:
   - ID employé (unique)
   - Nom et prénom
   - Poste
   - Date d'embauche
   - Catégorie salariale
   - Informations bancaires
3. Cliquez sur **Enregistrer**

---

### 3️⃣ Traitement de la Paie

**Accès:** Cliquez sur **💰 Paie** dans le menu

**Étapes pour traiter la paie mensuelle:**

1. **Créer une nouvelle période:**
   - Cliquez sur **+ Nouvelle Période**
   - Sélectionnez les dates (début, fin, paiement)
   - Les employés sont ajoutés automatiquement

2. **Vérifier/Modifier les données:**
   - Vérifiez les jours travaillés
   - Ajoutez les primes et indemnités variables
   - Modifiez les montants si nécessaire

3. **Calculer la paie:**
   - Cliquez sur **🔢 Calculer Tout**
   - Le système calcule automatiquement:
     - Salaire brut
     - INPS et AMO
     - Impôt sur le revenu (progressif)
     - Déductions de prêts
     - Net à payer

4. **Finaliser:**
   - Cliquez sur **✅ Finaliser la Période**
   - Une fois finalisée, la période est verrouillée

---

### 4️⃣ Prêts et Avances

**Accès:** Cliquez sur **💳 Prêts** dans le menu

**Pour accorder un prêt:**
1. Cliquez sur **+ Ajouter Prêt**
2. Sélectionnez l'employé
3. Choisissez le type (Prêt ou Avance)
4. Entrez le montant
5. Définissez la durée (utilisez les boutons rapides: 3, 6, 12, 18, 24, 36 mois)
6. La mensualité est calculée automatiquement
7. Cliquez sur **Enregistrer**

**Déduction automatique:**
- Les mensualités sont déduites automatiquement lors du traitement de la paie
- Le solde restant est mis à jour automatiquement

---

### 5️⃣ Génération de Rapports

**Accès:** Cliquez sur **📊 Rapports** dans le menu

**Rapports disponibles:**

1. **Bulletins de Paie (PDF)**
   - Pour un ou tous les employés
   - Format professionnel
   - Comprend tous les détails de calcul

2. **Récapitulatif de Paie**
   - Vue d'ensemble de tous les employés
   - Totaux et statistiques

3. **Liste de Virements Bancaires**
   - Pour effectuer les paiements
   - Format prêt pour la banque

4. **Charges Patronales**
   - INPS, AMO, taxes sociales
   - Montants à verser aux organismes

5. **Récapitulatif des Impôts**
   - ITS par employé
   - Total à reverser

6. **Export Excel**
   - Toutes les données exportées
   - Analyse et archivage

**Pour générer un rapport:**
1. Sélectionnez la période
2. Cliquez sur le rapport souhaité
3. Le PDF/Excel s'ouvre automatiquement

---

### 6️⃣ Paramètres Système

**Accès:** Cliquez sur **⚙️ Paramètres** dans le menu

**Configuration disponible:**
- 💰 Tranches d'imposition (ITS)
- 📊 Barème des salaires CCFC
- 🏢 Départements et agences
- 📈 Taux sociaux (INPS, AMO)

**⚠️ Attention:** Modifiez ces paramètres avec précaution!

---

## 🔐 Gestion de Votre Compte

### Changer votre mot de passe:

1. Si vous êtes **administrateur:**
   - Allez dans **Outils > Gestion des Utilisateurs**
   - Cliquez sur **🔑 Mot de passe** à côté de votre nom
   - Entrez le nouveau mot de passe

2. Sinon, contactez votre administrateur

### Déconnexion:

- Cliquez sur **🚪 Déconnexion** en bas de la barre latérale

---

## 👥 Pour les Administrateurs

### Créer des comptes utilisateurs:

1. Allez dans **Outils > Gestion des Utilisateurs**
2. Cliquez sur **+ Ajouter Utilisateur**
3. Remplissez les informations
4. Choisissez le rôle (Admin ou Utilisateur)
5. Définissez le mot de passe initial

### Configurer les permissions:

1. Dans la liste des utilisateurs
2. Cliquez sur **🔒 Permissions** pour un utilisateur
3. Cochez les permissions appropriées:
   - Consulter vs Modifier
   - Traiter la paie vs Lecture seule
   - Générer rapports vs Exporter données
4. Cliquez sur **💾 Enregistrer**

**Voir [PERMISSIONS_GUIDE.md](PERMISSIONS_GUIDE.md) pour plus de détails**

---

## 💡 Conseils et Astuces

### Organisation
- ✅ Traitez la paie à la même période chaque mois
- ✅ Finalisez les périodes une fois validées
- ✅ Archivez les bulletins PDF mensuellement

### Sécurité
- ✅ Utilisez des mots de passe forts
- ✅ Déconnectez-vous après utilisation
- ✅ Ne partagez jamais vos identifiants
- ✅ Sauvegardez régulièrement la base de données

### Performance
- ✅ Finalisez les anciennes périodes (améliore la vitesse)
- ✅ Exportez vers Excel pour analyses complexes
- ✅ Fermez l'application quand elle n'est pas utilisée

### Dépannage
- ❓ **L'application ne démarre pas:** Vérifiez les droits d'accès
- ❓ **Base de données verrouillée:** Un autre utilisateur modifie des données
- ❓ **Permission refusée:** Contactez votre administrateur
- ❓ **Calculs incorrects:** Vérifiez les paramètres système

---

## 📚 Workflow Mensuel Typique

### Semaine 1 du mois:
1. ✅ Créer la nouvelle période de paie
2. ✅ Vérifier que tous les employés sont présents

### Semaine 2-3:
3. ✅ Saisir les données variables (primes, absences, heures sup.)
4. ✅ Gérer les nouveaux prêts si nécessaire

### Semaine 4:
5. ✅ Calculer la paie pour tous les employés
6. ✅ Vérifier les montants
7. ✅ Générer les bulletins de paie PDF
8. ✅ Exporter la liste de virements bancaires
9. ✅ Finaliser la période

### Après paiement:
10. ✅ Archiver les bulletins
11. ✅ Générer le récapitulatif des charges patronales
12. ✅ Préparer les déclarations pour l'INPS, AMO, etc.

---

## 🆘 Besoin d'Aide?

### Documentation complète:
- [PERMISSIONS_GUIDE.md](PERMISSIONS_GUIDE.md) - Guide des permissions
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Guide de déploiement

### Support:
- Contactez votre administrateur système
- Consultez les messages d'erreur (ils contiennent des infos utiles)
- Vérifiez vos permissions si une action est bloquée

---

## ✅ Checklist Première Utilisation

- [ ] J'ai lancé l'application
- [ ] Je me suis connecté avec mes identifiants
- [ ] J'ai changé mon mot de passe par défaut (si admin)
- [ ] J'ai exploré le tableau de bord
- [ ] J'ai consulté la liste des employés
- [ ] J'ai vérifié mes permissions
- [ ] Je sais comment me déconnecter
- [ ] Je connais le workflow mensuel
- [ ] Je sais générer des bulletins de paie
- [ ] J'ai identifié mon administrateur en cas de problème

---

**Bienvenue dans PAIERO!** 🎉

**Version:** 1.0
**Date:** 2026-01-25
