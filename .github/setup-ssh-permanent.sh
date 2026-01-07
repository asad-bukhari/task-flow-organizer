#!/bin/bash
# Permanent SSH Key Setup for GitHub

echo "=== GitHub SSH Key Setup (Permanent) ==="
echo ""

# Start ssh-agent if not running
if [ -z "$SSH_AUTH_SOCK" ]; then
    echo "Starting ssh-agent..."
    eval "$(ssh-agent -s)"
fi

# Add SSH key
echo "Adding your SSH key to ssh-agent..."
echo "You'll be prompted for your key passphrase (this is a ONE-TIME setup)"
ssh-add ~/.ssh/id_ed25519

# Test connection
echo ""
echo "Testing SSH connection to GitHub..."
ssh -T git@github.com

# Update git remote to use SSH
echo ""
echo "Updating git remote to use SSH..."
cd /home/asad/code/ai-400/task-managment
git remote set-url origin git@github.com:asad-bukhari/task-management-api.git

echo ""
echo "✅ Setup complete! Your SSH key is now permanently loaded."
echo "You can push to GitHub without entering credentials."
echo ""
echo "To push, run: git push -u origin main"
