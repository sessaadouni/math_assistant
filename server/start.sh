#!/bin/bash

# 🚀 Script de démarrage Math RAG
# Lance le backend et le frontend en parallèle

set -e

echo "🎯 Démarrage Math RAG Application"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour vérifier si un port est utilisé
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port occupé
    else
        return 1  # Port libre
    fi
}

# Vérifier les dépendances
echo -e "${BLUE}📦 Vérification des dépendances...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 n'est pas installé${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js n'est pas installé${NC}"
    exit 1
fi

if ! command -v ollama &> /dev/null; then
    echo -e "${RED}❌ Ollama n'est pas installé${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Toutes les dépendances sont installées${NC}"
echo ""

# Vérifier les ports
echo -e "${BLUE}🔍 Vérification des ports...${NC}"

if check_port 8000; then
    echo -e "${YELLOW}⚠️  Port 8000 déjà utilisé (Backend)${NC}"
    read -p "Voulez-vous continuer quand même ? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

if check_port 3000; then
    echo -e "${YELLOW}⚠️  Port 3000 déjà utilisé (Frontend)${NC}"
    read -p "Voulez-vous continuer quand même ? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}✅ Ports disponibles${NC}"
echo ""

# Vérifier les modèles Ollama
echo -e "${BLUE}🤖 Vérification des modèles Ollama...${NC}"

if ! ollama list | grep -q "deepseek-v3.1:671b-cloud"; then
    echo -e "${YELLOW}⚠️  Modèle deepseek-v3.1:671b-cloud non trouvé${NC}"
    echo -e "${YELLOW}   Téléchargement du modèle (cela peut prendre du temps)...${NC}"
    ollama pull deepseek-v3.1:671b-cloud
fi

if ! ollama list | grep -q "mxbai-embed-large"; then
    echo -e "${YELLOW}⚠️  Modèle mxbai-embed-large non trouvé${NC}"
    echo -e "${YELLOW}   Téléchargement du modèle...${NC}"
    ollama pull mxbai-embed-large:latest
fi

echo -e "${GREEN}✅ Modèles Ollama prêts${NC}"
echo ""

# Fonction de nettoyage
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Arrêt des services...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✅ Services arrêtés${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Démarrer le backend
echo -e "${BLUE}🔴 Démarrage du backend FastAPI...${NC}"
cd "$(dirname "$0")"
python server.py > backend.log 2>&1 &
BACKEND_PID=$!

# Attendre que le backend soit prêt
echo -e "${YELLOW}⏳ Attente du backend...${NC}"
sleep 3

# Vérifier si le backend est démarré
if ! check_port 8000; then
    echo -e "${RED}❌ Le backend n'a pas démarré correctement${NC}"
    echo -e "${RED}   Voir backend.log pour plus de détails${NC}"
    cat backend.log
    exit 1
fi

echo -e "${GREEN}✅ Backend démarré sur http://localhost:8000${NC}"
echo ""

# Démarrer le frontend
echo -e "${BLUE}🟢 Démarrage du frontend Next.js...${NC}"
cd client

# Installer les dépendances si nécessaire
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installation des dépendances npm...${NC}"
    npm install
fi

npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

# Attendre que le frontend soit prêt
echo -e "${YELLOW}⏳ Attente du frontend...${NC}"
sleep 5

# Vérifier si le frontend est démarré
if ! check_port 3000; then
    echo -e "${RED}❌ Le frontend n'a pas démarré correctement${NC}"
    echo -e "${RED}   Voir frontend.log pour plus de détails${NC}"
    cat ../frontend.log
    cleanup
fi

echo -e "${GREEN}✅ Frontend démarré sur http://localhost:3000${NC}"
echo ""

# Afficher les URLs
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✨ Math RAG Application démarrée avec succès !${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  🌐 Frontend:    ${BLUE}http://localhost:3000${NC}"
echo -e "  🔌 Backend:     ${BLUE}http://localhost:8000${NC}"
echo -e "  ❤️  Health:      ${BLUE}http://localhost:8000/health${NC}"
echo ""
echo -e "${YELLOW}📝 Logs:${NC}"
echo -e "  Backend:  tail -f backend.log"
echo -e "  Frontend: tail -f frontend.log"
echo ""
echo -e "${RED}Pour arrêter: Ctrl+C${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test rapide du backend
echo -e "${BLUE}🧪 Test du backend...${NC}"
if curl -s http://localhost:8000/health | grep -q "ok"; then
    echo -e "${GREEN}✅ Backend répond correctement${NC}"
else
    echo -e "${YELLOW}⚠️  Le backend ne répond pas comme attendu${NC}"
fi
echo ""

# Ouvrir le navigateur (optionnel)
if command -v xdg-open &> /dev/null; then
    echo -e "${BLUE}🌐 Ouverture du navigateur...${NC}"
    xdg-open http://localhost:3000 2>/dev/null || true
elif command -v open &> /dev/null; then
    echo -e "${BLUE}🌐 Ouverture du navigateur...${NC}"
    open http://localhost:3000 2>/dev/null || true
fi

# Attendre indéfiniment
echo -e "${YELLOW}👀 Surveillance des processus...${NC}"
echo -e "${YELLOW}   (Appuyez sur Ctrl+C pour arrêter)${NC}"
echo ""

while true; do
    # Vérifier que les processus tournent toujours
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Le backend s'est arrêté !${NC}"
        echo -e "${RED}   Voir backend.log pour les détails${NC}"
        cleanup
    fi
    
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Le frontend s'est arrêté !${NC}"
        echo -e "${RED}   Voir frontend.log pour les détails${NC}"
        cleanup
    fi
    
    sleep 5
done
