# ⚪⚫ Jeu de Go Miniature 9x9 (Pygame)

Une adaptation épurée et moderne du traditionnel jeu de stratégie japonais **Go**, développée en **Python** avec **Pygame**.

---

## 📸 Fonctionnalités

- 🪵 **Goban traditionnel :** Plateau en bois de format 9x9 optimisé pour des parties rapides et tactiques.
- 🔗 **Gestion des libertés & Captures :** Algorithme intelligent calculant les groupes de pierres et capturant automatiquement les pierres sans liberté.
- 🚫 **Règle anti-suicide :** Empêche le placement d'une pierre sur une intersection sans issue, sauf si elle réalise une capture.
- ⏭️ **Bouton Passer :** Permet de passer son tour (deux passes consécutives mettent fin à la partie).

---

## 🚀 Lancement

```bash
pip install pygame
python main.py