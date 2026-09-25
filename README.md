# Guide : Automatiser l'acceptation des invitations GitHub avec Python

## Table des matières
1. [Installation des outils nécessaires](#installation-des-outils-nécessaires)
2. [Configuration du token d'accès](#configuration-du-token-daccès)
3. [Script Python automatisé](#script-python-automatisé)
4. [Utilisation du script](#utilisation-du-script)
5. [Dépannage](#dépannage)

---

## Installation des outils nécessaires

### 1. Installer GitHub CLI

Visitez https://cli.github.com/ et suivez les instructions d'installation en fonction de votre système.

**Vérifier l'installation :**
```bash
gh --version
```

### 2. Installer Python et les dépendances

**Créer un environnement virtuel :**
```bash
# Créer l'environnement virtuel
python -m venv github_invitations

# Activer l'environnement virtuel
# Linux/Mac :
source github_invitations/bin/activate

# Windows :
github_invitations\Scripts\activate
```

**Installer les dépendances :**
```bash
# Une fois l'environnement virtuel activé
pip install requests==2.34.2 PyGithub==2.10.0
```

**Note :** Vous devrez activer l'environnement virtuel à chaque fois que vous voulez utiliser le script :
```bash
# Linux/Mac
source github_invitations/bin/activate

# Windows
github_invitations\Scripts\activate
```

---

## Configuration du token d'accès

```bash
gh auth login
# Suivez les instructions interactives
# Choisissez "GitHub.com" → "HTTPS" → "Y" pour "Authenticate Git with your GitHub credentials?"
# → "Login with a web browser" -> Appuyez sur la touche <Entrée> 
# -> Entrez le One-time code affiché dans la console dans votre navigateur 
# -> "Authorize GitHub" 🎉
```

---

## Script Python automatisé

Créez un fichier `accepter_invitations.py` :

```python
import subprocess
import os
import requests

def get_github_token():
    """Récupère le token GitHub par ordre de priorité"""
    # 1. Variable d'environnement
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        print("✅ Token récupéré via variable d'environnement")
        return token
    
    # 2. GitHub CLI
    try:
        result = subprocess.run(['gh', 'auth', 'token'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            token = result.stdout.strip()
            print("✅ Token récupéré via GitHub CLI")
            return token
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️ GitHub CLI non trouvé ou non configuré")
    
    # 3. Saisie manuelle
    token = input("Entrez votre token GitHub: ").strip()
    return token

def validate_token(token):
    """Valide que le token fonctionne"""
    headers = {'Authorization': f'token {token}'}
    try:
        response = requests.get('https://api.github.com/user', headers=headers)
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Connecté en tant que: {user['login']}")
            return True
        else:
            print("❌ Token invalide")
            return False
    except:
        print("❌ Erreur de connexion")
        return False

def accept_invitations(token):
    """Accepte toutes les invitations GitHub en attente"""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        # Récupérer les invitations
        print("🔍 Recherche des invitations en attente...")
        response = requests.get('https://api.github.com/user/repository_invitations', headers=headers)
        response.raise_for_status()
        
        invitations = response.json()
        
        if not invitations:
            print("ℹ️ Aucune invitation en attente.")
            return
        
        print(f"📬 Trouvé {len(invitations)} invitation(s).")
        print("📋 Liste des dépôts:")
        for inv in invitations:
            print(f"   - {inv['repository']['full_name']}")
        
        print("\n🔄 Acceptation en cours...")
        
        accepted = 0
        failed = 0
        
        for invitation in invitations:
            try:
                # Accepter l'invitation
                patch_response = requests.patch(
                    f'https://api.github.com/user/repository_invitations/{invitation["id"]}',
                    headers=headers
                )
                
                if patch_response.status_code == 204:
                    print(f"✅ {invitation['repository']['full_name']}")
                    accepted += 1
                else:
                    print(f"❌ Erreur pour {invitation['repository']['full_name']} (Code: {patch_response.status_code})")
                    failed += 1
                    
            except Exception as e:
                print(f"❌ Erreur pour {invitation['repository']['full_name']}: {e}")
                failed += 1
        
        print(f"\n📊 Résumé:")
        print(f"   ✅ Acceptées: {accepted}")
        print(f"   ❌ Échecs: {failed}")
        print(f"   📝 Total: {len(invitations)}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des invitations: {e}")

def main():
    print("Automatisation des invitations GitHub")
    print("=" * 40)
    
    # Récupérer le token
    token = get_github_token()
    
    if not token:
        print("❌ Aucun token disponible")
        return
    
    # Valider le token
    if not validate_token(token):
        return
    
    # Accepter les invitations
    accept_invitations(token)
    
    print("\n✨ Terminé!")

if __name__ == "__main__":
    main()
```

---

## Utilisation du script

### 1. Lancer le script

```bash
python accepter_invitations.py
```

### 2. Exemple de sortie

```
Automatisation des invitations GitHub
========================================
✅ Token récupéré via GitHub CLI
✅ Connecté en tant que: votre_nom_utilisateur
🔍 Recherche des invitations en attente...
📬 Trouvé 12 invitation(s).
📋 Liste des dépôts:
   - etudiant1/projet-final
   - etudiant2/devoir-semaine3
   - etudiant3/tp-javascript
   ...

🔄 Acceptation en cours...
✅ etudiant1/projet-final
✅ etudiant2/devoir-semaine3
✅ etudiant3/tp-javascript
...

📊 Résumé:
   ✅ Acceptées: 12
   ❌ Échecs: 0
   📝 Total: 12

✨ Terminé!
```

---

## Dépannage

### Erreur "Token invalide"
- Relancez `gh auth login`

### Erreur "GitHub CLI non trouvé"
- Vérifiez l'installation avec `gh --version`

### Erreur de connexion
- Vérifiez votre connexion internet
- Vérifiez que GitHub est accessible

### Le script ne trouve aucune invitation
- Les invitations peuvent avoir expiré (après 7 jours)
- Vérifiez manuellement sur GitHub.com

---

*Guide simplifié pour automatiser la gestion des invitations GitHub avec Python en contexte éducatif.*
