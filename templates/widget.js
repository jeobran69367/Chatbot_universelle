// Widget JavaScript pour intégration facile
(function() {
    'use strict';
    
    // Configuration par défaut
    const defaultConfig = {
        apiUrl: 'http://localhost:5001/api',
        theme: 'blue',
        position: 'bottom-right',
        language: 'fr',
        title: '🤖 Assistant IA',
        welcomeMessage: 'Bonjour ! Comment puis-je vous aider ?'
    };
    
    // Configuration du widget (peut être surchargée)
    window.ChatbotConfig = window.ChatbotConfig || {};
    const config = Object.assign({}, defaultConfig, window.ChatbotConfig);
    
    // Styles CSS du widget
    const styles = `
        .chatbot-widget {
            position: fixed;
            ${config.position.includes('bottom') ? 'bottom: 20px;' : 'top: 20px;'}
            ${config.position.includes('right') ? 'right: 20px;' : 'left: 20px;'}
            width: 350px;
            height: 500px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            display: none;
            flex-direction: column;
            z-index: 10000;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .chatbot-header {
            background: ${getThemeGradient(config.theme)};
            color: white;
            padding: 15px;
            border-radius: 15px 15px 0 0;
            text-align: center;
            font-weight: bold;
            position: relative;
        }

        .chatbot-close {
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: white;
            font-size: 18px;
            cursor: pointer;
            padding: 5px;
        }

        .chatbot-messages {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            max-height: 350px;
        }

        .chatbot-message {
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 10px;
            max-width: 80%;
            animation: fadeIn 0.3s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .chatbot-message.user {
            background: ${getThemeColor(config.theme)};
            color: white;
            margin-left: auto;
            text-align: right;
        }

        .chatbot-message.bot {
            background: #f1f3f5;
            color: #333;
        }

        .chatbot-input {
            display: flex;
            padding: 15px;
            border-top: 1px solid #e9ecef;
        }

        .chatbot-input input {
            flex: 1;
            border: 1px solid #ddd;
            border-radius: 20px;
            padding: 10px 15px;
            outline: none;
            font-size: 14px;
        }

        .chatbot-input input:focus {
            border-color: ${getThemeColor(config.theme)};
        }

        .chatbot-input button {
            background: ${getThemeColor(config.theme)};
            color: white;
            border: none;
            border-radius: 20px;
            padding: 10px 15px;
            margin-left: 10px;
            cursor: pointer;
            font-size: 14px;
            transition: opacity 0.3s;
        }

        .chatbot-input button:hover {
            opacity: 0.9;
        }

        .chatbot-input button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }

        .chatbot-toggle {
            position: fixed;
            ${config.position.includes('bottom') ? 'bottom: 20px;' : 'top: 20px;'}
            ${config.position.includes('right') ? 'right: 20px;' : 'left: 20px;'}
            width: 60px;
            height: 60px;
            background: ${getThemeGradient(config.theme)};
            border-radius: 50%;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            z-index: 10001;
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }

        .chatbot-toggle:hover {
            transform: scale(1.1);
        }

        .chatbot-typing {
            display: none;
            padding: 10px;
            color: #666;
            font-style: italic;
            font-size: 14px;
        }

        .chatbot-typing.active {
            display: block;
        }

        .typing-dots {
            display: inline-block;
        }

        .typing-dots::after {
            content: '';
            animation: dots 2s infinite;
        }

        @keyframes dots {
            0%, 20% { content: '.'; }
            40% { content: '..'; }
            60% { content: '...'; }
            80%, 100% { content: ''; }
        }

        @media (max-width: 480px) {
            .chatbot-widget {
                width: 90vw;
                height: 70vh;
                bottom: 10px;
                right: 5vw;
                left: 5vw;
            }
            
            .chatbot-toggle {
                width: 50px;
                height: 50px;
                font-size: 20px;
            }
        }
    `;
    
    // HTML du widget
    const widgetHTML = `
        <div class="chatbot-toggle" onclick="ChatbotWidget.toggle()">💬</div>
        <div class="chatbot-widget" id="chatbot-widget">
            <div class="chatbot-header">
                ${config.title}
                <button class="chatbot-close" onclick="ChatbotWidget.close()">×</button>
            </div>
            <div class="chatbot-messages" id="chatbot-messages">
                <div class="chatbot-message bot">${config.welcomeMessage}</div>
            </div>
            <div class="chatbot-typing" id="chatbot-typing">
                L'assistant réfléchit<span class="typing-dots"></span>
            </div>
            <div class="chatbot-input">
                <input type="text" id="chatbot-input" placeholder="Tapez votre message..." />
                <button id="chatbot-send" onclick="ChatbotWidget.sendMessage()">Envoyer</button>
            </div>
        </div>
    `;
    
    // Fonctions utilitaires pour les thèmes
    function getThemeColor(theme) {
        const themes = {
            blue: '#667eea',
            green: '#56ccf2',
            purple: '#764ba2',
            orange: '#f093fb',
            red: '#ff6b6b'
        };
        return themes[theme] || themes.blue;
    }
    
    function getThemeGradient(theme) {
        const gradients = {
            blue: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            green: 'linear-gradient(135deg, #56ccf2 0%, #2f80ed 100%)',
            purple: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
            orange: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            red: 'linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%)'
        };
        return gradients[theme] || gradients.blue;
    }
    
    // Classe principale du widget
    class ChatbotWidget {
        constructor() {
            this.isOpen = false;
            this.isTyping = false;
            this.init();
        }
        
        init() {
            // Injecter les styles
            const styleElement = document.createElement('style');
            styleElement.textContent = styles;
            document.head.appendChild(styleElement);
            
            // Injecter le HTML
            const widgetContainer = document.createElement('div');
            widgetContainer.innerHTML = widgetHTML;
            document.body.appendChild(widgetContainer);
            
            // Ajouter les event listeners
            this.attachEventListeners();
        }
        
        attachEventListeners() {
            const input = document.getElementById('chatbot-input');
            const sendButton = document.getElementById('chatbot-send');
            
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !this.isTyping) {
                    this.sendMessage();
                }
            });
            
            // Auto-resize du widget sur mobile
            window.addEventListener('resize', this.handleResize.bind(this));
        }
        
        toggle() {
            if (this.isOpen) {
                this.close();
            } else {
                this.open();
            }
        }
        
        open() {
            const widget = document.getElementById('chatbot-widget');
            const toggle = document.querySelector('.chatbot-toggle');
            
            widget.style.display = 'flex';
            toggle.style.display = 'none';
            this.isOpen = true;
            
            // Focus sur l'input
            setTimeout(() => {
                document.getElementById('chatbot-input').focus();
            }, 100);
        }
        
        close() {
            const widget = document.getElementById('chatbot-widget');
            const toggle = document.querySelector('.chatbot-toggle');
            
            widget.style.display = 'none';
            toggle.style.display = 'block';
            this.isOpen = false;
        }
        
        async sendMessage() {
            if (this.isTyping) return;
            
            const input = document.getElementById('chatbot-input');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Afficher le message utilisateur
            this.addMessage(message, 'user');
            input.value = '';
            
            // Désactiver l'input pendant le traitement
            this.setInputState(false);
            this.showTyping(true);
            
            try {
                const response = await fetch(`${config.apiUrl}/chat`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    
                    // Petit délai pour effet plus naturel
                    setTimeout(() => {
                        this.addMessage(data.response, 'bot');
                        this.showTyping(false);
                        this.setInputState(true);
                    }, 1000);
                } else {
                    throw new Error('Erreur de réponse du serveur');
                }
            } catch (error) {
                console.error('Erreur chatbot:', error);
                this.addMessage('Désolé, une erreur s\'est produite. Veuillez réessayer.', 'bot');
                this.showTyping(false);
                this.setInputState(true);
            }
        }
        
        addMessage(text, sender) {
            const messagesContainer = document.getElementById('chatbot-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chatbot-message ${sender}`;
            messageDiv.textContent = text;
            
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        showTyping(show) {
            const typingIndicator = document.getElementById('chatbot-typing');
            this.isTyping = show;
            
            if (show) {
                typingIndicator.classList.add('active');
            } else {
                typingIndicator.classList.remove('active');
            }
        }
        
        setInputState(enabled) {
            const input = document.getElementById('chatbot-input');
            const button = document.getElementById('chatbot-send');
            
            input.disabled = !enabled;
            button.disabled = !enabled;
        }
        
        handleResize() {
            // Gérer le redimensionnement sur mobile
            if (window.innerWidth <= 480 && this.isOpen) {
                const widget = document.getElementById('chatbot-widget');
                widget.style.height = '70vh';
            }
        }
    }
    
    // Initialiser le widget quand le DOM est prêt
    function initWidget() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                window.ChatbotWidget = new ChatbotWidget();
            });
        } else {
            window.ChatbotWidget = new ChatbotWidget();
        }
    }
    
    // API publique
    window.ChatbotWidget = {
        toggle: function() {
            if (window.ChatbotWidget instanceof ChatbotWidget) {
                window.ChatbotWidget.toggle();
            }
        },
        open: function() {
            if (window.ChatbotWidget instanceof ChatbotWidget) {
                window.ChatbotWidget.open();
            }
        },
        close: function() {
            if (window.ChatbotWidget instanceof ChatbotWidget) {
                window.ChatbotWidget.close();
            }
        }
    };
    
    // Démarrer l'initialisation
    initWidget();
})();
