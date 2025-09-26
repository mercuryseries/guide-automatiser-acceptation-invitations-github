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
