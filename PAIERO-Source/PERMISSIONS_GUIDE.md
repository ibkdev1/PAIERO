# PAIERO - Guide du Système de Permissions

## Vue d'ensemble

Le système de permissions de PAIERO permet aux administrateurs de contrôler précisément ce que chaque utilisateur peut faire dans l'application.

## Types de Permissions

### 1. Gestion des Employés
- **can_view_employees**: Consulter la liste des employés
- **can_edit_employees**: Ajouter et modifier des employés
- **can_delete_employees**: Supprimer des employés

### 2. Gestion de la Paie
- **can_view_payroll**: Consulter les périodes de paie
- **can_process_payroll**: Créer des périodes et traiter la paie
- **can_finalize_payroll**: Finaliser les périodes de paie (verrouillage)

### 3. Gestion des Prêts & Avances
- **can_view_loans**: Consulter les prêts et avances
- **can_manage_loans**: Ajouter, modifier et supprimer des prêts

### 4. Rapports & Exports
- **can_generate_reports**: Générer des bulletins de paie et rapports PDF
- **can_export_data**: Exporter les données vers Excel

### 5. Paramètres Système
- **can_view_parameters**: Consulter les paramètres système
- **can_modify_parameters**: Modifier les tranches d'imposition et autres paramètres

### 6. Gestion des Utilisateurs
- **can_manage_users**: Gérer les comptes utilisateurs (réservé aux admins)

## Configuration des Permissions

### Pour les Administrateurs

1. Allez dans **Outils > Gestion des Utilisateurs**
2. Cliquez sur le bouton **🔒 Permissions** pour un utilisateur
3. Cochez/décochez les permissions souhaitées
4. Cliquez sur **💾 Enregistrer**

### Permissions par Défaut

**Administrateurs:**
- Toutes les permissions activées
- Accès complet à toutes les fonctionnalités
- Les admins contournent toujours les vérifications de permissions

**Utilisateurs Standard:**
- Lecture seule par défaut
- Peuvent consulter: employés, paie, prêts, générer des rapports
- Ne peuvent pas modifier les données ni exporter

## Comportement de l'Application

### Boutons et Menus
- Les boutons et fonctionnalités sans permission sont **masqués** automatiquement
- Si un utilisateur n'a pas de permissions d'édition, les boutons "Modifier" et "Supprimer" n'apparaissent pas

### Messages d'Erreur
- Si un utilisateur tente d'accéder à une fonctionnalité sans permission, un message s'affiche:
  > "Permission refusée: Vous n'avez pas la permission de [action]."

## Exemples d'Utilisation

### Exemple 1: Employé RH (Lecture/Édition)
**Permissions recommandées:**
- ✓ Consulter les employés
- ✓ Modifier les employés
- ✗ Supprimer les employés
- ✓ Consulter la paie
- ✗ Traiter la paie
- ✓ Générer des rapports
- ✗ Exporter des données

**Résultat:** L'employé peut gérer les informations des employés et consulter la paie, mais ne peut pas la modifier ni exporter de données sensibles.

### Exemple 2: Comptable
**Permissions recommandées:**
- ✓ Consulter les employés
- ✗ Modifier les employés
- ✓ Consulter la paie
- ✓ Traiter la paie
- ✓ Finaliser la paie
- ✓ Consulter les prêts
- ✓ Gérer les prêts
- ✓ Générer des rapports
- ✓ Exporter des données

**Résultat:** Le comptable peut traiter toute la paie et les prêts, mais ne peut pas modifier les informations des employés.

### Exemple 3: Auditeur (Lecture Seule)
**Permissions recommandées:**
- ✓ Consulter les employés
- ✗ Modifier les employés
- ✓ Consulter la paie
- ✗ Traiter la paie
- ✓ Consulter les prêts
- ✗ Gérer les prêts
- ✓ Générer des rapports
- ✗ Exporter des données

**Résultat:** L'auditeur peut tout consulter et générer des rapports, mais ne peut rien modifier.

## Sécurité

### Règles Importantes
1. **Les administrateurs ont toujours un accès complet**, quelle que soit la configuration des permissions
2. Un administrateur ne peut pas se désactiver lui-même
3. Un administrateur ne peut pas supprimer son propre compte
4. Les permissions sont vérifiées à chaque action

### Audit
Toutes les modifications de permissions sont enregistrées dans la base de données avec:
- Qui a fait la modification
- Quand elle a été faite
- Quelles permissions ont changé

## Migration

Si vous avez déjà des utilisateurs dans votre base de données, exécutez:

```bash
python3 database/migrate_permissions.py
```

Cela créera automatiquement:
- La table `user_permissions`
- Les permissions par défaut pour tous les utilisateurs existants
- Permissions complètes pour les admins
- Permissions de lecture seule pour les utilisateurs standards

## Structure Technique

### Base de Données
Table: `user_permissions`
- 13 colonnes de permissions (BOOLEAN)
- Clé étrangère vers `users`
- Déclencheur de mise à jour automatique

### Code
- `/database/auth.py`: Méthodes de vérification des permissions
- `/ui/dialogs/permissions_dialog.py`: Interface de gestion
- Tous les écrans: Vérifications intégrées

### API Principale

```python
# Vérifier une permission
if AuthManager.has_permission('can_edit_employees'):
    # Action autorisée
    pass

# Obtenir toutes les permissions d'un utilisateur
permissions = AuthManager.get_user_permissions(user_id)

# Définir les permissions
AuthManager.set_user_permissions(user_id, {
    'can_edit_employees': 1,
    'can_delete_employees': 0
})
```

## Support

Pour toute question sur le système de permissions, contactez l'administrateur système.

---

**Version:** 1.0
**Date:** 2026-01-25
**Auteur:** PAIERO Development Team
