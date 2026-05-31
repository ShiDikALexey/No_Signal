(function () {
    var currentUser = window.CURRENT_USER;
    var currentChatId = null;
    var socket = null;
    var chats = [];
    var typingTimers = {};
    var selectedGroupMembers = new Set();
    var selectedGroupNicknames = new Map();
    var modalMode = 'newChat';
    var onlineUsers = new Set();
    var pendingFile = null;
    var pendingFileData = null;
    var showingArchive = false;
    var mediaRecorder = null;
    var audioChunks = [];
    var audioContext = null;
    var analyser = null;
    var recordingStartTime = null;
    var recordingTimer = null;
    var waveformAnimation = null;
    var isRecording = false;
    var recordingCancelled = false;

    function escapeHtml(text) {
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    function parseMarkdown(text) {
        if (!text) return '';
        
        var escaped = escapeHtml(text);
        
        escaped = escaped.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        escaped = escaped.replace(/\*(.+?)\*/g, '<em>$1</em>');
        escaped = escaped.replace(/__(.+?)__/g, '<strong>$1</strong>');
        escaped = escaped.replace(/_(.+?)_/g, '<em>$1</em>');
        
        escaped = escaped.replace(/~~(.+?)~~/g, '<del>$1</del>');
        
        escaped = escaped.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        escaped = escaped.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        
        escaped = escaped.replace(/\[(.+?)\]\((.+?)\)/g, function(match, text, url) {
            if (/^(javascript|data|vbscript):/i.test(url)) return match;
            return '<a href="' + escapeHtml(url) + '" target="_blank" rel="noopener noreferrer nofollow">' + text + '</a>';
        });
        
        escaped = escaped.replace(/\n/g, '<br>');
        
        return escaped;
    }

    function showToast(message, type) {
        type = type || 'info';
        var container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }

        var toast = document.createElement('div');
        toast.className = 'toast toast-' + type;
        toast.innerHTML = '<span class="toast-message">' + escapeHtml(message) + '</span>' +
            '<button class="toast-close">&times;</button>';

        container.appendChild(toast);

        var closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', function() {
            toast.remove();
        });

        setTimeout(function() {
            toast.classList.add('toast-hiding');
            setTimeout(function() {
                toast.remove();
            }, 300);
        }, 4000);
    }

    function showConfirm(message, onConfirm) {
        var overlay = document.createElement('div');
        overlay.className = 'confirm-overlay';
        overlay.innerHTML = '<div class="confirm-dialog">' +
            '<div class="confirm-message">' + escapeHtml(message) + '</div>' +
            '<div class="confirm-buttons">' +
            '<button class="confirm-btn confirm-btn-cancel">Отмена</button>' +
            '<button class="confirm-btn confirm-btn-ok">Подтвердить</button>' +
            '</div></div>';

        document.body.appendChild(overlay);

        var cancelBtn = overlay.querySelector('.confirm-btn-cancel');
        var okBtn = overlay.querySelector('.confirm-btn-ok');

        cancelBtn.addEventListener('click', function() {
            overlay.remove();
        });

        okBtn.addEventListener('click', function() {
            overlay.remove();
            if (onConfirm) onConfirm();
        });

        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) overlay.remove();
        });
    }

    function api(method, url, data) {
        var token = document.querySelector('meta[name="csrf-token"]');
        var opts = {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin'
        };
        if (token) opts.headers['X-CSRFToken'] = token.content;
        if (data) opts.body = JSON.stringify(data);
        return fetch(url, opts).then(function (r) { return r.json(); });
    }

    function init() {
        initSocket();
        loadChats();
        renderCurrentUser();
        bindEvents();
        initMobileViewport();
    }

    function initSocket() {
        socket = io({
            transports: ['websocket'],
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: 50
        });
        socket.on('connect', function () {
            console.log('Socket connected');
            if (currentChatId) {
                socket.emit('join_chat', { chat_id: currentChatId });
            }
        });
        socket.on('disconnect', function (reason) {
            console.log('Socket disconnected:', reason);
        });
        socket.on('connect_error', function (err) {
            console.log('Socket connect error:', err.message);
        });
        socket.on('reconnect', function (attempt) {
            console.log('Socket reconnected after', attempt, 'attempts');
            if (currentChatId) {
                socket.emit('join_chat', { chat_id: currentChatId });
            }
        });
        socket.on('new_message', onNewMessage);
        socket.on('chat_updated', onChatUpdated);
        socket.on('new_chat', onNewChat);
        socket.on('user_typing', onUserTyping);
        socket.on('user_stopped_typing', onUserStoppedTyping);
        socket.on('user_online', onUserOnline);
        socket.on('user_offline', onUserOffline);
        socket.on('message_read', onMessageRead);
    }

    function renderCurrentUser() {
        var avatar = document.getElementById('my-avatar');
        var nickname = document.getElementById('my-nickname');
        if (avatar) {
            avatar.style.backgroundColor = currentUser.avatarColor;
            if (currentUser.avatarPhoto) {
                avatar.innerHTML = '<img src="' + escapeHtml(currentUser.avatarPhoto) + '" class="avatar-photo">';
            } else {
                avatar.textContent = currentUser.nickname.charAt(0).toUpperCase();
            }
        }
        if (nickname) {
            nickname.textContent = currentUser.nickname;
        }
    }

    function bindEvents() {
        document.getElementById('send-btn').addEventListener('click', sendMessage);
        document.getElementById('emoji-btn').addEventListener('click', toggleEmojiPicker);
        document.getElementById('attach-btn').addEventListener('click', function () {
            document.getElementById('file-input').click();
        });
        document.getElementById('file-input').addEventListener('change', handleFileSelect);
        document.getElementById('new-chat-btn').addEventListener('click', showNewChatModal);
        document.getElementById('modal-close').addEventListener('click', closeModal);
        document.getElementById('modal-overlay').addEventListener('click', function (e) {
            if (e.target === this) closeModal();
        });
        document.getElementById('user-info-trigger').addEventListener('click', toggleProfileDropdown);
        document.getElementById('user-info-trigger').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                toggleProfileDropdown();
            }
        });
        document.getElementById('btn-change-nickname').addEventListener('click', showChangeNickname);
        document.getElementById('btn-account-settings').addEventListener('click', showAccountSettings);
        document.getElementById('search-input').addEventListener('input', function () {
            renderChatList(this.value.trim().toLowerCase());
        });
        document.getElementById('archive-btn').addEventListener('click', function () {
            showingArchive = true;
            renderChatList();
        });
        document.getElementById('back-btn').addEventListener('click', function () {
            document.getElementById('chat-area').classList.remove('active');
            document.getElementById('chat-area').classList.remove('mobile-show');
            document.getElementById('sidebar').classList.remove('mobile-hidden');
            document.getElementById('no-chat-selected').classList.remove('hidden');
        });
        var chatHeaderProfile = document.getElementById('chat-header-profile');
        if (chatHeaderProfile) {
            chatHeaderProfile.addEventListener('click', function () {
                toggleProfileDropdown();
            });
            chatHeaderProfile.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleProfileDropdown();
                }
            });
        }
        document.getElementById('message-input').addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage();
            }
        });

var typingDebounce = null;
        document.getElementById('message-input').addEventListener('input', function () {
            if (!currentChatId) return;
            if (typingDebounce) clearTimeout(typingDebounce);
            socket.emit('typing', { chat_id: currentChatId });
            typingDebounce = setTimeout(function () {
                socket.emit('stop_typing', { chat_id: currentChatId });
            }, 2000);
        });

        var voiceBtn = document.getElementById('voice-btn');
        voiceBtn.addEventListener('mousedown', startVoiceRecording);
        voiceBtn.addEventListener('mouseup', stopVoiceRecording);
        voiceBtn.addEventListener('mouseleave', cancelVoiceRecording);
        voiceBtn.addEventListener('touchstart', function(e) {
            e.preventDefault();
            recordingCancelled = false;
            startVoiceRecording();
        });
        voiceBtn.addEventListener('touchend', function(e) {
            e.preventDefault();
            if (!recordingCancelled && isRecording) {
                stopVoiceRecording();
            }
        });
        voiceBtn.addEventListener('touchmove', function(e) {
            e.preventDefault();
            var touch = e.touches[0];
            var rect = voiceBtn.getBoundingClientRect();
            if (touch.clientY < rect.top - 80) {
                cancelVoiceRecording();
            }
        });

        document.getElementById('voice-recording-cancel').addEventListener('click', cancelVoiceRecording);

        var dragCounter = 0;
        document.addEventListener('dragenter', function(e) {
            e.preventDefault();
            dragCounter++;
            showDragOverlay();
        });
        document.addEventListener('dragleave', function(e) {
            e.preventDefault();
            dragCounter--;
            if (dragCounter === 0) hideDragOverlay();
        });
        document.addEventListener('dragover', function(e) {
            e.preventDefault();
        });
        document.addEventListener('drop', function(e) {
            e.preventDefault();
            dragCounter = 0;
            hideDragOverlay();
            if (!currentChatId) return;
            var files = e.dataTransfer.files;
            if (files.length > 0) sendFile(files[0]);
        });
    }

    function loadChats() {
        showChatListSkeleton();
        api('GET', '/api/chats').then(function (data) {
            chats = data;
            renderChatList();
        });
    }

    function showChatListSkeleton() {
        var list = document.getElementById('chat-list');
        if (!list || chats.length > 0) return;
        
        var skeletonHtml = '';
        for (var i = 0; i < 5; i++) {
            skeletonHtml += '<div class="skeleton-chat-item">' +
                '<div class="skeleton-avatar"></div>' +
                '<div class="skeleton-info">' +
                '<div class="skeleton-line skeleton-line-short"></div>' +
                '<div class="skeleton-line skeleton-line-long"></div>' +
                '</div></div>';
        }
        list.innerHTML = skeletonHtml;
    }

    function showMessagesSkeleton() {
        var container = document.getElementById('messages');
        if (!container) return;
        
        var skeletonHtml = '';
        for (var i = 0; i < 8; i++) {
            var isOwn = i % 3 === 0;
            skeletonHtml += '<div class="skeleton-message ' + (isOwn ? 'own' : 'other') + '">' +
                '<div class="skeleton-line skeleton-line-message"></div>' +
                '</div>';
        }
        container.innerHTML = skeletonHtml;
    }

    function renderChatList(filter) {
        var list = document.getElementById('chat-list');
        var archiveBtnWrapper = document.getElementById('archive-btn-wrapper');
        var filtered = chats;

        var existingArchiveHeader = list.parentNode.querySelector('.archive-header');
        if (existingArchiveHeader) existingArchiveHeader.remove();

        var archivedChats = chats.filter(function (c) { return c.is_archived; });
        var archiveCount = archivedChats.length;

        if (archiveCount > 0) {
            archiveBtnWrapper.classList.remove('hidden');
            var countEl = document.getElementById('archive-count');
            countEl.textContent = archiveCount;
            countEl.classList.remove('hidden');
        } else {
            archiveBtnWrapper.classList.add('hidden');
        }

        if (showingArchive) {
            filtered = archivedChats;
            list.innerHTML = '';

            var header = document.createElement('div');
            header.className = 'archive-header';
            header.innerHTML = '<button class="archive-back-btn" id="archive-back-btn">&#8592;</button>' +
                '<span class="archive-title">Архив</span>';
            list.parentNode.insertBefore(header, list);

            document.getElementById('archive-back-btn').addEventListener('click', function () {
                showingArchive = false;
                renderChatList();
            });
        } else {
            filtered = chats.filter(function (c) { return !c.is_archived; });

            if (filter) {
                filtered = filtered.filter(function (c) {
                    return c.name.toLowerCase().indexOf(filter) !== -1;
                });
            }

            var pinned = filtered.filter(function (c) { return c.is_pinned; });
            var unpinned = filtered.filter(function (c) { return !c.is_pinned; });
            filtered = pinned.concat(unpinned);
        }

        list.innerHTML = '';
        if (filtered.length === 0) {
            var emptyMsg = document.createElement('div');
            emptyMsg.className = 'chat-list-empty';
            emptyMsg.textContent = showingArchive ? 'Архив пуст' : (filter ? 'Ничего не найдено' : 'Нет чатов. Нажмите + чтобы начать');
            list.appendChild(emptyMsg);
            return;
        }

        filtered.forEach(function (chat) {
            list.appendChild(createChatListItem(chat));
        });
    }

    function createChatListItem(chat) {
        var div = document.createElement('div');
        div.className = 'chat-item' + (chat.id === currentChatId ? ' active' : '') + (chat.is_pinned ? ' pinned' : '');
        div.dataset.chatId = chat.id;

        var letter = chat.name.charAt(0).toUpperCase();
        var lastMsg = chat.last_message;
        var lastMsgText = lastMsg ? lastMsg.prefix + ': ' + lastMsg.text : 'Нет сообщений';
        var lastMsgTime = lastMsg ? lastMsg.timestamp : '';

        var badges = '';
        if (chat.is_pinned) badges += '<span class="chat-badge-icon">📌</span>';
        if (chat.is_muted) badges += '<span class="chat-badge-icon">🔕</span>';

        var avatarHtml;
        if (chat.avatar_photo) {
            avatarHtml = '<div class="chat-avatar" style="background-color:' + escapeHtml(chat.avatar_color) + '"><img src="' + escapeHtml(chat.avatar_photo) + '" class="avatar-photo"></div>';
        } else {
            avatarHtml = '<div class="chat-avatar" style="background-color:' + escapeHtml(chat.avatar_color) + '">' + escapeHtml(letter) + '</div>';
        }

        div.innerHTML =
            avatarHtml +
            '<div class="chat-info">' +
            '<div class="chat-item-name">' + escapeHtml(chat.name) + (chat.is_group ? ' <span class="online-dot" style="background:var(--accent);width:6px;height:6px;"></span>' : '') + '</div>' +
            '<div class="chat-item-preview">' + escapeHtml(lastMsgText) + '</div>' +
            '</div>' +
            '<div class="chat-item-meta">' +
            '<span class="chat-item-time">' + escapeHtml(lastMsgTime) + '</span>' +
            (chat.is_group ? '<span class="chat-item-badge">' + chat.members_count + '</span>' : '') +
            (badges ? '<div class="chat-item-badges">' + badges + '</div>' : '') +
            '</div>';

        div.addEventListener('click', function () {
            selectChat(chat.id);
        });

        div.addEventListener('contextmenu', function (e) {
            e.preventDefault();
            e.stopPropagation();
            showChatContextMenu(e.clientX, e.clientY, chat);
        });

        var longPressTimer = null;
        div.addEventListener('touchstart', function (e) {
            var touch = e.touches[0];
            longPressTimer = setTimeout(function () {
                showChatContextMenu(touch.clientX, touch.clientY, chat);
            }, 500);
        });
        div.addEventListener('touchend', function () {
            clearTimeout(longPressTimer);
        });
        div.addEventListener('touchmove', function () {
            clearTimeout(longPressTimer);
        });

        return div;
    }

    function selectChat(chatId) {
        currentChatId = chatId;

        document.querySelectorAll('.chat-item').forEach(function (el) {
            el.classList.toggle('active', parseInt(el.dataset.chatId) === chatId);
        });

        document.getElementById('no-chat-selected').classList.add('hidden');
        document.getElementById('chat-area').classList.add('active');
        document.getElementById('sidebar').classList.add('mobile-hidden');
        document.getElementById('chat-area').classList.add('mobile-show');

        var chat = chats.find(function (c) { return c.id === chatId; });
        if (chat) updateChatHeader(chat);

        showMessagesSkeleton();
        api('GET', '/api/chats/' + chatId + '/messages').then(function (data) {
            var messages = data.messages || data;
            renderMessages(messages, chat ? chat.is_group : false);
        });

        socket.emit('join_chat', { chat_id: chatId });
        socket.emit('mark_read', { chat_id: chatId });

        document.getElementById('message-input').focus();
        hideTypingIndicator();
    }

    function updateChatHeader(chat) {
        var info = document.getElementById('chat-header-info');
        var letter = chat.name.charAt(0).toUpperCase();
        var avatarHtml;
        if (chat.avatar_photo) {
            avatarHtml = '<div class="chat-avatar small" style="background-color:' + escapeHtml(chat.avatar_color) + '"><img src="' + escapeHtml(chat.avatar_photo) + '" class="avatar-photo"></div>';
        } else {
            avatarHtml = '<div class="chat-avatar small" style="background-color:' + escapeHtml(chat.avatar_color) + '">' + escapeHtml(letter) + '</div>';
        }
        info.innerHTML =
            '<div class="header-chat-info">' +
            avatarHtml +
            '<div>' +
            '<div class="header-chat-name">' + escapeHtml(chat.name) + '</div>' +
            '<div class="header-chat-status" id="header-status">' +
            (chat.is_group ? chat.members_count + ' участников' : 'offline') +
            '</div>' +
            '</div>' +
            '</div>';
    }

    function renderMessages(messages, isGroup) {
        var container = document.getElementById('messages');
        container.innerHTML = '';
        var lastDate = null;
        var lastSenderId = null;

        messages.forEach(function (msg) {
            var msgDate = msg.full_timestamp ? msg.full_timestamp.split('T')[0] : null;
            if (msgDate && msgDate !== lastDate) {
                appendDateSeparator(msgDate);
                lastDate = msgDate;
                lastSenderId = null;
            }

            var isGrouped = (msg.sender_id === lastSenderId);
            appendMessage(msg, false, isGrouped, isGroup);
            lastSenderId = msg.sender_id;
        });
        scrollToBottom();
    }

    function appendDateSeparator(dateStr) {
        var container = document.getElementById('messages');
        if (!container) return;

        var date = new Date(dateStr);
        var today = new Date();
        var yesterday = new Date();
        yesterday.setDate(yesterday.getDate() - 1);

        var label;
        if (date.toDateString() === today.toDateString()) {
            label = 'Сегодня';
        } else if (date.toDateString() === yesterday.toDateString()) {
            label = 'Вчера';
        } else {
            label = date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' });
        }

        var div = document.createElement('div');
        div.className = 'date-separator';
        div.innerHTML = '<span class="date-separator-text">' + label + '</span>';
        container.appendChild(div);
    }

    function appendMessage(msg, animate, isGrouped, isGroup) {
        var container = document.getElementById('messages');
        if (!container) return;

        var isOwn = msg.sender_id === currentUser.id;
        var div = document.createElement('div');
        var fileHtml = renderFileContent(msg);
        var groupedClass = isGrouped ? ' message-grouped' : '';

        if (isOwn) {
            div.className = 'message own' + groupedClass;
            div.dataset.msgId = msg.id;
            var statusHtml = '';
            if (!isGroup) {
                if (msg.is_read) {
                    statusHtml = '<span class="msg-status msg-status-read" title="Прочитано">✓✓</span>';
                } else {
                    statusHtml = '<span class="msg-status msg-status-sent" title="Доставлено">✓✓</span>';
                }
            }
            div.innerHTML =
                (msg.text ? '<div class="msg-text">' + parseMarkdown(msg.text) + '</div>' : '') +
                fileHtml +
                '<div class="msg-time">' + escapeHtml(msg.timestamp) + statusHtml + '</div>';
        } else {
            div.className = 'message other' + groupedClass;
            var senderHtml = isGrouped ? '' : '<div class="msg-sender" style="color:' + escapeHtml(msg.sender_avatar_color) + '">' + escapeHtml(msg.sender_nickname) + '</div>';
            div.innerHTML =
                senderHtml +
                (msg.text ? '<div class="msg-text">' + parseMarkdown(msg.text) + '</div>' : '') +
                fileHtml +
                '<div class="msg-time">' + escapeHtml(msg.timestamp) + '</div>';
        }

        container.appendChild(div);

        if (msg.file_type === 'image' && msg.file_url) {
            var img = div.querySelector('.msg-file-image');
            if (img) {
                img.addEventListener('click', function () {
                    openLightbox(this.src);
                });
            }
        }

        if (msg.file_type === 'audio' && msg.file_url) {
            var playBtn = div.querySelector('.audio-play-btn');
            if (playBtn) {
                playBtn.addEventListener('click', function () {
                    playAudioMessage(this);
                });
            }
        }

        if (animate !== false) scrollToBottom();
    }

    function renderFileContent(msg) {
        if (!msg.file_url) return '';

        if (msg.file_type === 'image') {
            return '<div class="msg-file"><img src="' + escapeHtml(msg.file_url) + '" class="msg-file-image" alt="' + escapeHtml(msg.file_name) + '"></div>';
        }

        if (msg.file_type === 'audio') {
            return renderAudioMessage(msg);
        }

        var icon = getFileIcon(msg.file_type);
        return '<div class="msg-file"><a href="' + escapeHtml(msg.file_url) + '" class="msg-file-card" download="' + escapeHtml(msg.file_name) + '" target="_blank">' +
            '<div class="msg-file-icon">' + icon + '</div>' +
            '<div class="msg-file-details">' +
            '<div class="msg-file-name">' + escapeHtml(msg.file_name) + '</div>' +
            '<div class="msg-file-size">' + formatFileSize(msg.file_size) + '</div>' +
            '</div>' +
            '</a></div>';
    }

    function getFileIcon(fileType) {
        switch (fileType) {
            case 'video': return '🎬';
            case 'audio': return '🎵';
            case 'document': return '📄';
            case 'archive': return '📦';
            default: return '📎';
        }
    }

    function scrollToBottom() {
        var container = document.getElementById('messages');
        if (container) {
            container.scrollTop = container.scrollHeight;
        }
    }

    function sendMessage() {
        var input = document.getElementById('message-input');
        var text = input.value.trim();

        if ((!text && !pendingFile) || !currentChatId) return;

        if (pendingFile) {
            var preview = document.getElementById('file-preview');
            preview.innerHTML = '<div class="upload-progress"><div class="upload-progress-bar" id="upload-bar" style="width:30%"></div></div>';

            uploadFile(pendingFile).then(function (result) {
                if (result.error) {
                    showToast(result.error, 'error');
                    removeFilePreview();
                    return;
                }
                socket.emit('send_message', {
                    chat_id: currentChatId,
                    text: text,
                    file_url: result.file_url,
                    file_name: result.file_name,
                    file_type: result.file_type,
                    file_size: result.file_size
                });
                removeFilePreview();
                input.value = '';
                input.focus();
                socket.emit('stop_typing', { chat_id: currentChatId });
            });
        } else {
            socket.emit('send_message', { chat_id: currentChatId, text: text });
            input.value = '';
            input.focus();
            socket.emit('stop_typing', { chat_id: currentChatId });
        }
    }

    function onNewMessage(msg) {
        var chat = chats.find(function (c) { return c.id === msg.chat_id; });
        var isGroup = chat ? chat.is_group : false;
        if (msg.chat_id === currentChatId) {
            appendMessage(msg, true, false, isGroup);
            socket.emit('mark_read', { chat_id: currentChatId });
        }
        loadChats();
    }

    function onMessageRead(data) {
        var msgEl = document.querySelector('.message.own[data-msg-id="' + data.message_id + '"]');
        if (msgEl) {
            var status = msgEl.querySelector('.msg-status');
            if (status) {
                status.className = 'msg-status msg-status-read';
                status.title = 'Прочитано';
            }
        }
    }

    function onChatUpdated(chatData) {
        var idx = chats.findIndex(function (c) { return c.id === chatData.id; });
        if (idx >= 0) {
            chats[idx] = chatData;
        } else {
            chats.unshift(chatData);
        }
        renderChatList(document.getElementById('search-input').value.trim().toLowerCase());
    }

    function onNewChat(chatData) {
        var exists = chats.some(function (c) { return c.id === chatData.id; });
        if (!exists) {
            chats.unshift(chatData);
            renderChatList();
        }
    }

    function onUserTyping(data) {
        if (data.chat_id !== currentChatId) return;
        var key = data.user_id;
        if (typingTimers[key]) clearTimeout(typingTimers[key]);
        showTypingIndicator(data.nickname);
        typingTimers[key] = setTimeout(function () {
            delete typingTimers[key];
            if (Object.keys(typingTimers).length === 0) hideTypingIndicator();
        }, 3000);
    }

    function onUserStoppedTyping(data) {
        if (data.chat_id !== currentChatId) return;
        delete typingTimers[data.user_id];
        if (Object.keys(typingTimers).length === 0) hideTypingIndicator();
    }

    function showTypingIndicator(nickname) {
        var el = document.getElementById('typing-indicator');
        if (el) {
            el.innerHTML =
                '<span>' + escapeHtml(nickname) + ' печатает</span>' +
                '<span class="typing-dots">' +
                '<span class="typing-dot"></span>' +
                '<span class="typing-dot"></span>' +
                '<span class="typing-dot"></span>' +
                '</span>';
            el.classList.remove('hidden');
        }
    }

    function hideTypingIndicator() {
        var el = document.getElementById('typing-indicator');
        if (el) {
            el.classList.add('hidden');
        }
    }

    function onUserOnline(data) {
        onlineUsers.add(data.user_id);
    }

    function onUserOffline(data) {
        onlineUsers.delete(data.user_id);
    }

    // ========== Modal ==========

    function closeModal() {
        document.getElementById('modal-overlay').classList.add('hidden');
        selectedGroupMembers = new Set();
        selectedGroupNicknames = new Map();
    }

    function showNewChatModal() {
        modalMode = 'newChat';
        var overlay = document.getElementById('modal-overlay');
        var content = document.getElementById('modal-content');
        var title = document.getElementById('modal-title');
        title.textContent = 'Новый чат';

        content.innerHTML =
            '<div class="modal-tabs">' +
            '<button class="modal-tab active" id="tab-private">Личный чат</button>' +
            '<button class="modal-tab" id="tab-group">Групповой чат</button>' +
            '</div>' +
            '<div id="tab-private-content">' +
            '<div class="modal-search"><input type="text" id="user-search" placeholder="Поиск по никнейму..." autocomplete="off"></div>' +
            '<div class="user-list" id="user-list"></div>' +
            '</div>' +
            '<div id="tab-group-content" class="hidden">' +
            '<div class="group-form">' +
            '<input type="text" id="group-name" placeholder="Название группы">' +
            '<div class="modal-search"><input type="text" id="group-user-search" placeholder="Добавить участников..." autocomplete="off"></div>' +
            '<div class="group-members" id="group-members"></div>' +
            '<div class="user-list" id="group-user-list"></div>' +
            '<button class="btn-create" id="create-group-btn" disabled>Создать группу</button>' +
            '</div>' +
            '</div>';

        overlay.classList.remove('hidden');

        document.getElementById('tab-private').addEventListener('click', function () {
            modalMode = 'newChat';
            this.classList.add('active');
            document.getElementById('tab-group').classList.remove('active');
            document.getElementById('tab-private-content').classList.remove('hidden');
            document.getElementById('tab-group-content').classList.add('hidden');
        });

        document.getElementById('tab-group').addEventListener('click', function () {
            modalMode = 'newGroup';
            this.classList.add('active');
            document.getElementById('tab-private').classList.remove('active');
            document.getElementById('tab-group-content').classList.remove('hidden');
            document.getElementById('tab-private-content').classList.add('hidden');
        });

        loadUsersForPrivateChat(null);
        loadUsersForGroupChat(null);

        document.getElementById('user-search').addEventListener('input', function () {
            loadUsersForPrivateChat(this.value.trim());
        });

        document.getElementById('group-user-search').addEventListener('input', function () {
            loadUsersForGroupChat(this.value.trim());
        });

        document.getElementById('create-group-btn').addEventListener('click', createGroupChat);
    }

    function loadUsersForPrivateChat(query) {
        var list = document.getElementById('user-list');
        if (!list) return;

        if (!query) {
            list.innerHTML = '<div class="chat-list-empty">Начните вводить никнейм для поиска</div>';
            return;
        }

        var url = '/api/users?q=' + encodeURIComponent(query);

        api('GET', url).then(function (users) {
            if (!list) return;
            list.innerHTML = '';

            if (users.length === 0) {
                list.innerHTML = '<div class="chat-list-empty">Пользователи не найдены</div>';
                return;
            }

            users.forEach(function (u) {
                var item = document.createElement('div');
                item.className = 'user-list-item';
                var avatarHtml;
                if (u.avatar_photo) {
                    avatarHtml = '<div class="chat-avatar small" style="background-color:' + escapeHtml(u.avatar_color) + '"><img src="' + escapeHtml(u.avatar_photo) + '" class="avatar-photo"></div>';
                } else {
                    avatarHtml = '<div class="chat-avatar small" style="background-color:' + escapeHtml(u.avatar_color) + '">' + escapeHtml(u.nickname.charAt(0).toUpperCase()) + '</div>';
                }
                item.innerHTML =
                    avatarHtml +
                    '<div class="user-item-info">' +
                    '<div class="user-item-nickname">' + escapeHtml(u.nickname) + (u.is_online ? ' <span class="online-dot"></span>' : '') + '</div>' +
                    '<div class="user-item-status' + (u.is_online ? ' online' : '') + '">' + (u.is_online ? 'В сети' : 'Не в сети') + '</div>' +
                    '</div>';
                item.addEventListener('click', function (e) {
                    e.stopPropagation();
                    startPrivateChat(u.id);
                });
                list.appendChild(item);
            });
        }).catch(function () {
            if (list) list.innerHTML = '<div class="chat-list-empty">Ошибка загрузки</div>';
        });
    }

    function loadUsersForGroupChat(query) {
        var list = document.getElementById('group-user-list');
        if (!list) return;

        if (!query) {
            list.innerHTML = '<div class="chat-list-empty">Начните вводить никнейм для поиска</div>';
            return;
        }

        var url = '/api/users?q=' + encodeURIComponent(query);

        api('GET', url).then(function (users) {
            if (!list) return;
            list.innerHTML = '';

            if (users.length === 0) {
                list.innerHTML = '<div class="chat-list-empty">Пользователи не найдены</div>';
                return;
            }

            users.forEach(function (u) {
                var item = document.createElement('div');
                item.className = 'user-list-item';
                var isSelected = selectedGroupMembers.has(u.id);
                if (isSelected) item.style.background = 'var(--bg-active)';
                item.innerHTML =
                    '<div class="chat-avatar small" style="background-color:' + escapeHtml(u.avatar_color) + '">' + escapeHtml(u.nickname.charAt(0).toUpperCase()) + '</div>' +
                    '<div class="user-item-info">' +
                    '<div class="user-item-nickname">' + escapeHtml(u.nickname) + (u.is_online ? ' <span class="online-dot"></span>' : '') + '</div>' +
                    '<div class="user-item-status' + (u.is_online ? ' online' : '') + '">' + (u.is_online ? 'В сети' : 'Не в сети') + '</div>' +
                    '</div>' +
                    '<div style="margin-left:auto;font-size:1.2em;color:' + (isSelected ? 'var(--accent)' : 'var(--text-muted)') + '">' + (isSelected ? '&#10003;' : '') + '</div>';
                item.addEventListener('click', function (e) {
                    e.stopPropagation();
                    toggleGroupMember(u.id, u.nickname, u.avatar_color);
                });
                list.appendChild(item);
            });
        }).catch(function () {
            if (list) list.innerHTML = '<div class="chat-list-empty">Ошибка загрузки</div>';
        });
    }

    function toggleGroupMember(id, nickname, color) {
        if (selectedGroupMembers.has(id)) {
            selectedGroupMembers.delete(id);
        } else {
            selectedGroupMembers.add(id);
            selectedGroupNicknames.set(id, nickname);
        }
        renderGroupMembers();
        loadUsersForGroupChat();
        var btn = document.getElementById('create-group-btn');
        if (btn) btn.disabled = selectedGroupMembers.size === 0;
    }

    function renderGroupMembers() {
        var container = document.getElementById('group-members');
        if (!container) return;
        container.innerHTML = '';
        selectedGroupMembers.forEach(function (id) {
            var nick = selectedGroupNicknames.get(id) || ('Участник #' + id);
            var chip = document.createElement('div');
            chip.className = 'group-member-chip';
            chip.dataset.userId = id;
            chip.innerHTML = '<span>' + escapeHtml(nick) + '</span><span class="chip-remove" data-remove-id="' + id + '">&times;</span>';
            container.appendChild(chip);
        });

        container.querySelectorAll('.chip-remove').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                var rid = parseInt(this.dataset.removeId);
                selectedGroupMembers.delete(rid);
                selectedGroupNicknames.delete(rid);
                renderGroupMembers();
                loadUsersForGroupChat();
                var cbtn = document.getElementById('create-group-btn');
                if (cbtn) cbtn.disabled = selectedGroupMembers.size === 0;
            });
        });
    }

    function startPrivateChat(userId) {
        api('POST', '/api/chats/private/' + userId).then(function (chat) {
            if (chat.error) {
                showToast(chat.error, 'error');
                return;
            }
            closeModal();
            var exists = chats.some(function (c) { return c.id === chat.id; });
            if (!exists) {
                chats.unshift(chat);
                renderChatList();
            }
            selectChat(chat.id);
        }).catch(function (err) {
            console.error('startPrivateChat error:', err);
            showToast('Ошибка создания чата', 'error');
        });
    }

    function createGroupChat() {
        var name = document.getElementById('group-name').value.trim();
        var members = Array.from(selectedGroupMembers);

        if (members.length === 0) return;

        api('POST', '/api/chats/group', { name: name, members: members }).then(function (chat) {
            if (chat.error) {
                showToast(chat.error, 'error');
                return;
            }
            closeModal();
            var exists = chats.some(function (c) { return c.id === chat.id; });
            if (!exists) {
                chats.unshift(chat);
                renderChatList();
            }
            selectChat(chat.id);
        }).catch(function (err) {
            console.error('createGroupChat error:', err);
            showToast('Ошибка создания группы', 'error');
        });
    }

    var EMOJI_DATA = {
        'Smileys': ['😀','😃','😄','😁','😆','😅','🤣','😂','🙂','🙃','😉','😊','😇','🥰','😍','🤩','😘','😗','😚','😙','🥲','😋','😛','😜','🤪','😝','🤑','🤗','🤭','🤫','🤔','🫡','🤐','🤨','😐','😑','😶','🫥','😏','😒','🙄','😬','🤥','😌','😔','😪','🤤','😴','😷','🤒','🤕','🤢','🤮','🥵','🥶','🥴','😵','🤯','🤠','🥳','🥸','😎','🤓','🧐'],
        'Gestures': ['👋','🤚','🖐','✋','🖖','🫱','🫲','🫳','🫴','👌','🤌','🤏','✌','🤞','🫰','🤟','🤘','🤙','👈','👉','👆','🖕','👇','☝','🫵','👍','👎','✊','👊','🤛','🤜','👏','🙌','🫶','👐','🤲','🤝','🙏','✍','💅','🤳','💪','🦾','🦿','🦵','🦶','👂','🦻','👃','🧠','🫀','🫁','🦷','🦴','👀','👁','👅','👄'],
        'Hearts': ['❤','🧡','💛','💚','💙','💜','🖤','🤍','🤎','💔','❤‍🔥','❤‍🩹','❣','💕','💞','💓','💗','💖','💘','💝','💟','♥','🫶','😍','🥰','😘','💑','💏'],
        'Animals': ['🐶','🐱','🐭','🐹','🐰','🦊','🐻','🐼','🐻‍❄','🐨','🐯','🦁','🐮','🐷','🐸','🐵','🙈','🙉','🙊','🐒','🐔','🐧','🐦','🐤','🐣','🐥','🦆','🦅','🦉','🦇','🐺','🐗','🐴','🦄','🐝','🪱','🐛','🦋','🐌','🐞','🐜','🪰','🪲','🪳','🦟','🦗','🕷','🦂','🐢','🐍','🦎','🦖','🦕','🐙','🦑','🦐','🦞','🦀','🐡','🐠','🐟','🐬','🐳','🐋','🦈','🐊','🐅','🐆','🦓','🦍','🦧','🐘','🦛','🦏','🐪','🐫','🦒','🦘','🦬','🐃','🐂','🐄','🐎','🐖','🐏','🐑','🦙','🐐','🦌','🐕','🐩','🦮','🐈','🐓','🦃','🦤','🦚','🦜','🦢','🦩','🕊','🐇','🦝','🦨','🦡','🦫','🦦','🦥','🐁','🐀','🐿','🦔'],
        'Food': ['🍏','🍎','🍐','🍊','🍋','🍌','🍉','🍇','🍓','🫐','🍈','🍒','🍑','🥭','🍍','🥥','🥝','🍅','🍆','🥑','🥦','🥬','🥒','🌶','🫑','🌽','🥕','🫒','🧄','🧅','🥔','🍠','🥐','🥯','🍞','🥖','🥨','🧀','🥚','🍳','🧈','🥞','🧇','🥓','🥩','🍗','🍖','🦴','🌭','🍔','🍟','🍕','🫓','🥪','🥙','🧆','🌮','🌯','🫔','🥗','🥘','🫕','🥫','🍝','🍜','🍲','🍛','🍣','🍱','🥟','🦪','🍤','🍙','🍚','🍘','🍥','🥠','🥮','🍢','🍡','🍧','🍨','🍦','🥧','🧁','🍰','🎂','🍮','🍭','🍬','🍫','🍿','🍩','🍪','🌰','🥜','🍯','🥛','🍼','🫖','☕','🍵','🧃','🥤','🧋','🍶','🍺','🍻','🥂','🍷','🥃','🍸','🍹','🧉','🍾','🧊','🥄','🍴','🍽','🥣','🥡','🥢','🧂'],
        'Travel': ['🚗','🚕','🚙','🚌','🚎','🏎','🚓','🚑','🚒','🚐','🛻','🚚','🚛','🚜','🏍','🛵','🚲','🛴','🛺','🚔','🚍','🚘','🚖','🛞','🚡','🚠','🚟','🚃','🚋','🚞','🚝','🚄','🚅','🚈','🚂','🚆','🚇','🚊','🚉','✈','🛫','🛬','🛩','💺','🛰','🚀','🛸','🚁','🛶','⛵','🚤','🛥','🛳','⛴','🚢','🗼','🏰','🏯','🏟','🎡','🎢','🎠','⛲','⛱','🏖','🏝','🏜','🌋','⛰','🏔','🗻','🏕','⛺','🛖','🏠','🏡','🏘','🏚','🏗','🏭','🏢','🏬','🏣','🏤','🏥','🏦','🏨','🏪','🏫','🏩','💒','🏛','⛪','🕌','🕍','🛕','🕋','⛩','🛤','🛣','🗾','🎑','🏞','🌅','🌄','🌠','🎇','🎆','🌇','🌆','🏙','🌃','🌌','🌉','🌁'],
        'Objects': ['⌚','📱','💻','⌨','🖥','🖨','🖱','🖲','🕹','🗜','💽','💾','💿','📀','📼','📷','📸','📹','🎥','📽','🎞','📞','☎','📟','📠','📺','📻','🎙','🎚','🎛','🧭','⏱','⏲','⏰','🕰','⌛','⏳','📡','🔋','🔌','💡','🔦','🕯','🪔','🧯','🛢','💸','💵','💴','💶','💷','🪙','💰','💳','💎','⚖','🪜','🧰','🪛','🔧','🔨','⚒','🛠','⛏','🪚','🔩','⚙','🪤','🧱','⛓','🧲','🔫','💣','🧨','🪓','🔪','🗡','⚔','🛡','🚬','⚰','🪦','⚱','🏺','🔮','📿','🧿','🪬','💈','⚗','🔭','🔬','🕳','🩹','🩺','💊','💉','🩸','🧬','🦠','🧫','🧪','🌡','🧹','🪠','🧺','🧻','🚽','🚰','🚿','🛁','🛀','🧼','🪥','🪒','🧽','🪣','🧴','🛎','🔑','🗝','🚪','🪑','🛋','🛏','🛌','🧸','🪆','🖼','🪞','🪟','🛍','🛒','🎁','🎈','🎏','🎀','🪄','🪅','🎊','🎉','🎎','🏮','🎐','🧧','✉','📩','📨','📧','💌','📥','📤','📦','🏷','🪧','📪','📫','📬','📭','📮','📯','📜','📃','📄','📑','🧾','📊','📈','📉','🗒','🗓','📆','📅','🗑','📇','🗃','🗳','🗄','📋','📁','📂','🗂','🗞','📰','📓','📔','📒','📕','📗','📘','📙','📚','📖','🔖','🧷','🔗','📎','🖇','📐','📏','🧮','📌','📍','✂','🖊','🖋','✒','🖌','🖍','📝','✏','🔍','🔎','🔏','🔐','🔒','🔓'],
        'Symbols': ['❤','🧡','💛','💚','💙','💜','🖤','🤍','🤎','💔','❣','💕','💞','💓','💗','💖','💘','💝','☮','✝','☪','🕉','☸','✡','🔯','🕎','☯','☦','🛐','⛎','♈','♉','♊','♋','♌','♍','♎','♏','♐','♑','♒','♓','🆔','⚛','🉑','☢','☣','📴','📳','🈶','🈚','🈸','🈺','🈷','✴','🆚','💮','🉐','㊙','㊗','🈴','🈵','🈹','🈲','🅰','🅱','🆎','🆑','🅾','🆘','❌','⭕','🛑','⛔','📛','🚫','💯','💢','♨','🚷','🚯','🚳','🚱','🔞','📵','🚭','❗','❕','❓','❔','‼','⁉','🔅','🔆','〽','⚠','🚸','🔱','⚜','🔰','♻','✅','🈯','💹','❇','✳','❎','🌐','💠','Ⓜ','🌀','💤','🏧','🚾','♿','🅿','🛗','🈳','🈂','🛂','🛃','🛄','🛅','🚹','🚺','🚼','⚧','🚻','🚮','🎦','📶','🈁','🔣','ℹ','🔤','🔡','🔠','🆖','🆗','🆙','🆒','🆕','🆓','0⃣','1⃣','2⃣','3⃣','4⃣','5⃣','6⃣','7⃣','8⃣','9⃣','🔟','🔢','#⃣','*⃣','⏏','▶','⏸','⏯','⏹','⏺','⏭','⏮','⏩','⏪','⏫','⏬','◀','🔼','🔽','➡','⬅','⬆','⬇','↗','↘','↙','↖','↕','↔','↪','↩','⤴','⤵','🔀','🔁','🔂','🔄','🔃','🎵','🎶','➕','➖','➗','✖','🟰','♾','💲','💱','™','©','®','〰','➰','➿','🔚','🔙','🔛','🔝','🔜','✔','☑','🔘','🔴','🟠','🟡','🟢','🔵','🟣','⚫','⚪','🟤','🔺','🔻','🔸','🔹','🔶','🔷','🔳','🔲','▪','▫','◾','◽','◼','◻','🟥','🟧','🟨','🟩','🟦','🟪','⬛','⬜','🟫','🔈','🔇','🔉','🔊','🔔','🔕','📣','📢','👁‍🗨','💬','💭','🗯','♠','♣','♥','♦','🃏','🎴','🀄','🕐','🕑','🕒','🕓','🕔','🕕','🕖','🕗','🕘','🕙','🕚','🕛']
    };

    var emojiPickerOpen = false;

    function toggleEmojiPicker() {
        var picker = document.getElementById('emoji-picker');
        if (picker.classList.contains('hidden')) {
            renderEmojiPicker();
            picker.classList.remove('hidden');
            emojiPickerOpen = true;
        } else {
            picker.classList.add('hidden');
            emojiPickerOpen = false;
        }
    }

    function renderEmojiPicker(filter) {
        var picker = document.getElementById('emoji-picker');
        var categories = Object.keys(EMOJI_DATA);

        var html = '<div class="emoji-picker-header">' +
            '<input type="text" class="emoji-picker-search" id="emoji-search" placeholder="Поиск эмодзи..." autocomplete="off">' +
            '</div>' +
            '<div class="emoji-categories">';

        categories.forEach(function (cat, i) {
            var icon = EMOJI_DATA[cat][0];
            html += '<button class="emoji-category-btn' + (i === 0 ? ' active' : '') + '" data-category="' + cat + '">' + icon + '</button>';
        });

        html += '</div><div class="emoji-grid" id="emoji-grid">';

        if (filter) {
            categories.forEach(function (cat) {
                EMOJI_DATA[cat].forEach(function (emoji) {
                    html += '<button class="emoji-item" data-emoji="' + emoji + '">' + emoji + '</button>';
                });
            });
        } else {
            var firstCat = categories[0];
            html += '<div class="emoji-category-title">' + firstCat + '</div>';
            EMOJI_DATA[firstCat].forEach(function (emoji) {
                html += '<button class="emoji-item" data-emoji="' + emoji + '">' + emoji + '</button>';
            });
        }

        html += '</div>';
        picker.innerHTML = html;

        document.getElementById('emoji-search').addEventListener('input', function () {
            renderEmojiGrid(this.value.trim());
        });

        picker.querySelectorAll('.emoji-category-btn').forEach(function (btn) {
            btn.addEventListener('click', function () {
                picker.querySelectorAll('.emoji-category-btn').forEach(function (b) { b.classList.remove('active'); });
                this.classList.add('active');
                renderEmojiGrid(null, this.dataset.category);
            });
        });

        picker.querySelectorAll('.emoji-item').forEach(function (btn) {
            btn.addEventListener('click', function () {
                insertEmoji(this.dataset.emoji);
            });
        });
    }

    function renderEmojiGrid(filter, category) {
        var grid = document.getElementById('emoji-grid');
        if (!grid) return;

        var html = '';

        if (filter) {
            Object.keys(EMOJI_DATA).forEach(function (cat) {
                EMOJI_DATA[cat].forEach(function (emoji) {
                    html += '<button class="emoji-item" data-emoji="' + emoji + '">' + emoji + '</button>';
                });
            });
        } else if (category) {
            html += '<div class="emoji-category-title">' + category + '</div>';
            EMOJI_DATA[category].forEach(function (emoji) {
                html += '<button class="emoji-item" data-emoji="' + emoji + '">' + emoji + '</button>';
            });
        } else {
            var categories = Object.keys(EMOJI_DATA);
            categories.forEach(function (cat) {
                html += '<div class="emoji-category-title">' + cat + '</div>';
                EMOJI_DATA[cat].forEach(function (emoji) {
                    html += '<button class="emoji-item" data-emoji="' + emoji + '">' + emoji + '</button>';
                });
            });
        }

        grid.innerHTML = html;

        grid.querySelectorAll('.emoji-item').forEach(function (btn) {
            btn.addEventListener('click', function () {
                insertEmoji(this.dataset.emoji);
            });
        });
    }

    function insertEmoji(emoji) {
        var input = document.getElementById('message-input');
        var start = input.selectionStart;
        var end = input.selectionEnd;
        var text = input.value;
        input.value = text.substring(0, start) + emoji + text.substring(end);
        input.selectionStart = input.selectionEnd = start + emoji.length;
        input.focus();
    }

    function handleFileSelect(e) {
        if (e.target.files.length > 0) {
            pendingFile = e.target.files[0];
            showFilePreview(pendingFile);
        }
    }

    function showFilePreview(file) {
        var preview = document.getElementById('file-preview');
        var html = '';

        if (file.type.startsWith('image/')) {
            var reader = new FileReader();
            reader.onload = function (e) {
                preview.innerHTML =
                    '<img src="' + e.target.result + '" class="file-preview-image">' +
                    '<div class="file-preview-info">' +
                    '<div class="file-preview-name">' + escapeHtml(file.name) + '</div>' +
                    '<div class="file-preview-size">' + formatFileSize(file.size) + '</div>' +
                    '</div>' +
                    '<button class="file-preview-remove" id="remove-file-btn">&times;</button>';
                document.getElementById('remove-file-btn').addEventListener('click', removeFilePreview);
            };
            reader.readAsDataURL(file);
        } else {
            html =
                '<div class="file-preview-info">' +
                '<div class="file-preview-name">' + escapeHtml(file.name) + '</div>' +
                '<div class="file-preview-size">' + formatFileSize(file.size) + '</div>' +
                '</div>' +
                '<button class="file-preview-remove" id="remove-file-btn">&times;</button>';
            preview.innerHTML = html;
            document.getElementById('remove-file-btn').addEventListener('click', removeFilePreview);
        }

        preview.classList.remove('hidden');
    }

    function removeFilePreview() {
        pendingFile = null;
        pendingFileData = null;
        document.getElementById('file-preview').classList.add('hidden');
        document.getElementById('file-preview').innerHTML = '';
        document.getElementById('file-input').value = '';
    }

    function uploadFile(file) {
        var formData = new FormData();
        formData.append('file', file);
        var token = document.querySelector('meta[name="csrf-token"]');
        if (token) formData.append('csrf_token', token.content);

        return fetch('/api/upload', {
            method: 'POST',
            body: formData,
            credentials: 'same-origin'
        }).then(function (r) { return r.json(); });
    }

    function sendFile(file) {
        uploadFile(file).then(function(data) {
            if (data.error) { showToast(data.error, 'error'); return; }
            socket.emit('send_message', {
                chat_id: currentChatId,
                file_url: data.file_url,
                file_name: data.file_name,
                file_type: data.file_type,
                file_size: data.file_size
            });
        });
    }

    function showDragOverlay() {
        if (document.querySelector('.drag-overlay')) return;
        var overlay = document.createElement('div');
        overlay.className = 'drag-overlay';
        overlay.innerHTML = '<div class="drag-overlay-text">Перетащите файл сюда</div>';
        document.body.appendChild(overlay);
    }

    function hideDragOverlay() {
        var overlay = document.querySelector('.drag-overlay');
        if (overlay) overlay.remove();
    }

    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' Б';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' КБ';
        return (bytes / (1024 * 1024)).toFixed(1) + ' МБ';
    }

    function openLightbox(url) {
        var lightbox = document.createElement('div');
        lightbox.className = 'image-lightbox';
        lightbox.id = 'lightbox-active';
        lightbox.innerHTML =
            '<button class="lightbox-close" id="lightbox-close">&times;</button>' +
            '<img src="' + escapeHtml(url) + '">';
        document.body.appendChild(lightbox);

        document.getElementById('lightbox-close').addEventListener('click', closeLightbox);
        lightbox.addEventListener('click', function(e) {
            if (e.target === lightbox) closeLightbox();
        });
        document.addEventListener('keydown', function lightboxEsc(e) {
            if (e.key === 'Escape') {
                closeLightbox();
                document.removeEventListener('keydown', lightboxEsc);
            }
        });
    }

    function closeLightbox() {
        var lb = document.getElementById('lightbox-active');
        if (lb) lb.remove();
    }

    // ========== Context Menu ==========

    function showChatContextMenu(x, y, chat) {
        hideContextMenu();

        var menu = document.createElement('div');
        menu.className = 'context-menu';
        menu.id = 'context-menu';

        var pinText = chat.is_pinned ? 'Открепить' : 'Закрепить';
        var pinIcon = chat.is_pinned ? '📌' : '📌';
        var archiveText = chat.is_archived ? 'Из архива' : 'В архив';
        var archiveIcon = chat.is_archived ? '📤' : '📥';
        var muteText = chat.is_muted ? 'Со звуком' : 'Без звука';
        var muteIcon = chat.is_muted ? '🔔' : '🔕';

        menu.innerHTML =
            '<button class="context-menu-item" data-action="pin">' +
            '<span class="context-menu-icon">' + pinIcon + '</span>' +
            '<span>' + pinText + '</span>' +
            '</button>' +
            '<button class="context-menu-item" data-action="archive">' +
            '<span class="context-menu-icon">' + archiveIcon + '</span>' +
            '<span>' + archiveText + '</span>' +
            '</button>' +
            '<button class="context-menu-item" data-action="mute">' +
            '<span class="context-menu-icon">' + muteIcon + '</span>' +
            '<span>' + muteText + '</span>' +
            '</button>' +
            '<div class="context-menu-divider"></div>' +
            '<button class="context-menu-item danger" data-action="clear">' +
            '<span class="context-menu-icon">🗑</span>' +
            '<span>Очистить историю</span>' +
            '</button>' +
            '<button class="context-menu-item danger" data-action="delete">' +
            '<span class="context-menu-icon">❌</span>' +
            '<span>Удалить чат</span>' +
            '</button>';

        document.body.appendChild(menu);

        var menuRect = menu.getBoundingClientRect();
        var viewportWidth = window.innerWidth;
        var viewportHeight = window.innerHeight;

        var left = x;
        var top = y;

        if (left + menuRect.width > viewportWidth) {
            left = viewportWidth - menuRect.width - 10;
        }
        if (left < 10) {
            left = 10;
        }
        if (top + menuRect.height > viewportHeight) {
            top = viewportHeight - menuRect.height - 10;
        }
        if (top < 10) {
            top = 10;
        }

        menu.style.left = left + 'px';
        menu.style.top = top + 'px';

        menu.querySelectorAll('.context-menu-item').forEach(function (item) {
            item.addEventListener('click', function () {
                var action = this.dataset.action;
                handleContextMenuAction(action, chat);
                hideContextMenu();
            });
        });

        document.addEventListener('click', hideContextMenu, { once: true });
    }

    function hideContextMenu() {
        var menu = document.getElementById('context-menu');
        if (menu) menu.remove();
    }

    function handleContextMenuAction(action, chat) {
        if (action === 'pin') {
            api('POST', '/api/chats/' + chat.id + '/pin').then(function (result) {
                if (result.error) return;
                loadChats();
            });
        } else if (action === 'archive') {
            api('POST', '/api/chats/' + chat.id + '/archive').then(function (result) {
                if (result.error) return;
                loadChats();
            });
        } else if (action === 'mute') {
            api('POST', '/api/chats/' + chat.id + '/mute').then(function (result) {
                if (result.error) return;
                loadChats();
            });
        } else if (action === 'clear') {
            showConfirm('Очистить всю историю сообщений?', function() {
                api('POST', '/api/chats/' + chat.id + '/clear').then(function (result) {
                    if (result.error) return;
                    if (currentChatId === chat.id) {
                        renderMessages([]);
                    }
                    loadChats();
                    showToast('История очищена', 'success');
                });
            });
        } else if (action === 'delete') {
            showConfirm('Удалить этот чат?', function() {
                api('DELETE', '/api/chats/' + chat.id).then(function (result) {
                    if (result.error) return;
                    if (currentChatId === chat.id) {
                        currentChatId = null;
                        document.getElementById('chat-area').classList.remove('active');
                        document.getElementById('no-chat-selected').classList.remove('hidden');
                    }
                    loadChats();
                    showToast('Чат удалён', 'success');
                });
            });
        }
    }

    // ========== Profile Dropdown ==========

    function toggleProfileDropdown() {
        var dropdown = document.getElementById('profile-dropdown');
        var trigger = document.getElementById('user-info-trigger');
        if (dropdown.classList.contains('hidden')) {
            renderProfileDropdown();
            dropdown.classList.remove('hidden');
            if (trigger) trigger.setAttribute('aria-expanded', 'true');
        } else {
            dropdown.classList.add('hidden');
            if (trigger) trigger.setAttribute('aria-expanded', 'false');
        }
    }

    function renderProfileDropdown() {
        var avatar = document.getElementById('dropdown-avatar');
        var name = document.getElementById('dropdown-name');
        var status = document.getElementById('dropdown-status');

        avatar.style.backgroundColor = currentUser.avatarColor;
        if (currentUser.avatarPhoto) {
            avatar.innerHTML = '<img src="' + escapeHtml(currentUser.avatarPhoto) + '" class="avatar-photo">';
        } else {
            avatar.textContent = currentUser.nickname.charAt(0).toUpperCase();
        }
        name.textContent = currentUser.nickname;
        status.textContent = currentUser.status || 'Нет статуса';
    }

    function showChangeNickname() {
        document.getElementById('profile-dropdown').classList.add('hidden');
        var overlay = document.getElementById('modal-overlay');
        var title = document.getElementById('modal-title');
        var content = document.getElementById('modal-content');

        title.textContent = 'Смена никнейма';
        content.innerHTML =
            '<div class="nickname-change-form">' +
            '<label>Новый никнейм</label>' +
            '<input type="text" id="nickname-input" value="' + escapeHtml(currentUser.nickname) + '" maxlength="30" autocomplete="off">' +
            '<div class="nickname-hint">От 2 до 30 символов</div>' +
            '<div class="nickname-buttons">' +
            '<button class="btn-cancel" id="nickname-cancel">Отмена</button>' +
            '<button class="btn-save" id="nickname-save">Сохранить</button>' +
            '</div></div>';

        overlay.classList.remove('hidden');

        var input = document.getElementById('nickname-input');
        input.focus();
        input.select();

        document.getElementById('nickname-cancel').addEventListener('click', closeModal);
        document.getElementById('nickname-save').addEventListener('click', function () {
            var newNickname = input.value.trim();
            if (!newNickname || newNickname === currentUser.nickname) {
                closeModal();
                return;
            }
            api('POST', '/auth/api/profile/nickname', { nickname: newNickname }).then(function (result) {
                if (result.error) {
                    showToast(result.error, 'error');
                    return;
                }
                currentUser.nickname = result.nickname;
                window.CURRENT_USER.nickname = result.nickname;
                renderCurrentUser();
                closeModal();
                showToast('Никнейм изменён', 'success');
            });
        });

        input.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') document.getElementById('nickname-save').click();
        });
    }

    function showAccountSettings() {
        document.getElementById('profile-dropdown').classList.add('hidden');

        api('GET', '/auth/api/profile').then(function (profile) {
            var overlay = document.getElementById('modal-overlay');
            var title = document.getElementById('modal-title');
            var content = document.getElementById('modal-content');

            title.textContent = 'Данные аккаунта';

            var avatarPreviewHtml;
            if (profile.avatar_photo) {
                avatarPreviewHtml = '<div class="avatar-upload-preview" style="background-color:' + escapeHtml(profile.avatar_color) + '"><img src="' + escapeHtml(profile.avatar_photo) + '"></div>';
            } else {
                avatarPreviewHtml = '<div class="avatar-upload-preview" style="background-color:' + escapeHtml(profile.avatar_color) + '">' + escapeHtml(profile.nickname.charAt(0).toUpperCase()) + '</div>';
            }

            var html = '<div class="settings-section">' +
                '<div class="settings-section-title">Фото профиля</div>' +
                '<div class="avatar-upload-section">' +
                avatarPreviewHtml +
                '<div class="avatar-upload-buttons">' +
                '<button class="avatar-upload-btn" id="upload-avatar-btn">Загрузить фото</button>' +
                '<input type="file" id="avatar-file-input" accept="image/*" hidden>' +
                (profile.avatar_photo ? '<button class="avatar-upload-btn danger" id="delete-avatar-btn">Удалить фото</button>' : '') +
                '</div>' +
                '</div>' +
                '</div>';

            html += '<div class="settings-section">' +
                '<div class="settings-section-title">Статус</div>' +
                '<div class="settings-field">' +
                '<input type="text" id="settings-status" placeholder="Что у вас нового?" maxlength="100" value="' + escapeHtml(profile.status || '') + '">' +
                '</div>' +
                '<button class="settings-btn" id="save-status-btn">Сохранить статус</button>' +
                '</div>';

            html += '<div class="settings-section">' +
                '<div class="settings-section-title">Цвет аватара</div>' +
                '<div class="color-picker-grid" id="color-picker">';

            profile.avatar_colors.forEach(function (color) {
                var activeClass = color === profile.avatar_color ? ' active' : '';
                html += '<div class="color-picker-item' + activeClass + '" style="background-color:' + color + '" data-color="' + color + '"></div>';
            });

            html += '</div></div>';

            html += '<div class="settings-section">' +
                '<div class="settings-section-title">Смена пароля</div>' +
                '<div class="settings-field">' +
                '<label>Текущий пароль</label>' +
                '<input type="password" id="settings-old-password" placeholder="Введите текущий пароль">' +
                '</div>' +
                '<div class="settings-field">' +
                '<label>Новый пароль</label>' +
                '<input type="password" id="settings-new-password" placeholder="Минимум 6 символов">' +
                '</div>' +
                '<div class="settings-field">' +
                '<label>Подтвердите пароль</label>' +
                '<input type="password" id="settings-confirm-password" placeholder="Повторите новый пароль">' +
                '</div>' +
                '<button class="settings-btn" id="save-password-btn">Сменить пароль</button>' +
                '</div>';

            html += '<div class="settings-section">' +
                '<div class="settings-section-title">Удаление аккаунта</div>' +
                '<div class="settings-field">' +
                '<label>Введите пароль для подтверждения</label>' +
                '<input type="password" id="settings-delete-password" placeholder="Ваш пароль">' +
                '</div>' +
                '<button class="settings-btn danger" id="delete-account-btn">Удалить аккаунт</button>' +
                '</div>';

            content.innerHTML = html;
            overlay.classList.remove('hidden');

            document.getElementById('upload-avatar-btn').addEventListener('click', function () {
                document.getElementById('avatar-file-input').click();
            });

            document.getElementById('avatar-file-input').addEventListener('change', function (e) {
                if (e.target.files.length === 0) return;
                var file = e.target.files[0];
                var formData = new FormData();
                formData.append('file', file);
                var token = document.querySelector('meta[name="csrf-token"]');
                if (token) formData.append('csrf_token', token.content);

                fetch('/auth/api/profile/avatar-photo', {
                    method: 'POST',
                    body: formData,
                    credentials: 'same-origin'
                }).then(function (r) { return r.json(); }).then(function (result) {
                    if (result.error) {
                        showToast(result.error, 'error');
                        return;
                    }
                    currentUser.avatarPhoto = result.avatar_photo;
                    window.CURRENT_USER.avatarPhoto = result.avatar_photo;
                    renderCurrentUser();
                    showAccountSettings();
                    showToast('Фото обновлено', 'success');
                });
            });

            var deleteAvatarBtn = document.getElementById('delete-avatar-btn');
            if (deleteAvatarBtn) {
                deleteAvatarBtn.addEventListener('click', function () {
                    api('DELETE', '/auth/api/profile/avatar-photo').then(function (result) {
                        if (result.error) {
                            showToast(result.error, 'error');
                            return;
                        }
                        currentUser.avatarPhoto = '';
                        window.CURRENT_USER.avatarPhoto = '';
                        renderCurrentUser();
                        showAccountSettings();
                        showToast('Фото удалено', 'success');
                    });
                });
            }

            document.getElementById('save-status-btn').addEventListener('click', function () {
                var status = document.getElementById('settings-status').value.trim();
                api('POST', '/auth/api/profile/status', { status: status }).then(function (result) {
                    if (result.error) {
                        showToast(result.error, 'error');
                        return;
                    }
                    currentUser.status = result.status;
                    window.CURRENT_USER.status = result.status;
                    showToast('Статус обновлён', 'success');
                });
            });

            document.querySelectorAll('#color-picker .color-picker-item').forEach(function (item) {
                item.addEventListener('click', function () {
                    var color = this.dataset.color;
                    api('POST', '/auth/api/profile/avatar-color', { color: color }).then(function (result) {
                        if (result.error) {
                            showToast(result.error, 'error');
                            return;
                        }
                        currentUser.avatarColor = result.avatar_color;
                        window.CURRENT_USER.avatarColor = result.avatar_color;
                        renderCurrentUser();
                        document.querySelectorAll('#color-picker .color-picker-item').forEach(function (i) {
                            i.classList.remove('active');
                        });
                        item.classList.add('active');
                    });
                });
            });

            document.getElementById('save-password-btn').addEventListener('click', function () {
                var oldPwd = document.getElementById('settings-old-password').value;
                var newPwd = document.getElementById('settings-new-password').value;
                var confirmPwd = document.getElementById('settings-confirm-password').value;

                api('POST', '/auth/api/profile/password', {
                    old_password: oldPwd,
                    new_password: newPwd,
                    confirm_password: confirmPwd
                }).then(function (result) {
                    if (result.error) {
                        showToast(result.error, 'error');
                        return;
                    }
                    showToast('Пароль успешно изменён', 'success');
                    document.getElementById('settings-old-password').value = '';
                    document.getElementById('settings-new-password').value = '';
                    document.getElementById('settings-confirm-password').value = '';
                });
            });

            document.getElementById('delete-account-btn').addEventListener('click', function () {
                var pwd = document.getElementById('settings-delete-password').value;
                if (!pwd) {
                    showToast('Введите пароль', 'error');
                    return;
                }
                showConfirm('Вы уверены, что хотите удалить аккаунт? Это действие необратимо!', function() {
                    api('POST', '/auth/api/profile/delete', { password: pwd }).then(function (result) {
                        if (result.error) {
                            showToast(result.error, 'error');
                            return;
                        }
                        window.location.href = '/auth/login';
                    });
                });
            });
        });
    }

    function startVoiceRecording() {
        if (isRecording) return;

        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(function(stream) {
                isRecording = true;
                recordingCancelled = false;
                audioChunks = [];

                mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });

                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                analyser = audioContext.createAnalyser();
                var source = audioContext.createMediaStreamSource(stream);
                source.connect(analyser);
                analyser.fftSize = 64;

                mediaRecorder.ondataavailable = function(e) {
                    audioChunks.push(e.data);
                };

                mediaRecorder.onstop = function() {
                    stream.getTracks().forEach(function(track) { track.stop(); });
                    if (audioContext) {
                        audioContext.close();
                        audioContext = null;
                    }
                };

                mediaRecorder.start();
                recordingStartTime = Date.now();

                document.getElementById('voice-recording-overlay').classList.remove('hidden');
                document.getElementById('voice-btn').classList.add('recording');

                recordingTimer = setInterval(updateRecordingTime, 100);
                waveformAnimation = requestAnimationFrame(animateWaveform);

                createWaveformBars();
            })
            .catch(function(err) {
                console.error('Ошибка доступа к микрофону:', err);
                showToast('Не удалось получить доступ к микрофону', 'error');
            });
    }

    function stopVoiceRecording() {
        if (!isRecording || recordingCancelled) return;

        isRecording = false;
        clearInterval(recordingTimer);
        cancelAnimationFrame(waveformAnimation);

        mediaRecorder.stop();

        setTimeout(function() {
            var audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            var audioFile = new File([audioBlob], 'voice_' + Date.now() + '.webm', { type: 'audio/webm' });

            document.getElementById('voice-recording-overlay').classList.add('hidden');
            document.getElementById('voice-btn').classList.remove('recording');

            sendVoiceMessage(audioFile);
        }, 100);
    }

    function cancelVoiceRecording() {
        if (!isRecording) return;

        recordingCancelled = true;
        isRecording = false;
        clearInterval(recordingTimer);
        cancelAnimationFrame(waveformAnimation);

        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
        }

        document.getElementById('voice-recording-overlay').classList.add('hidden');
        document.getElementById('voice-btn').classList.remove('recording');
        document.getElementById('voice-waveform').innerHTML = '';
        document.getElementById('recording-time').textContent = '00:00';
    }

    function updateRecordingTime() {
        var elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
        var minutes = Math.floor(elapsed / 60);
        var seconds = elapsed % 60;
        var timeStr = (minutes < 10 ? '0' : '') + minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
        document.getElementById('recording-time').textContent = timeStr;
    }

    function createWaveformBars() {
        var waveform = document.getElementById('voice-waveform');
        waveform.innerHTML = '';
        for (var i = 0; i < 15; i++) {
            var bar = document.createElement('div');
            bar.className = 'wave-bar';
            bar.style.height = '4px';
            waveform.appendChild(bar);
        }
    }

    function animateWaveform() {
        if (!analyser || !isRecording) return;

        var dataArray = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(dataArray);

        var bars = document.querySelectorAll('.wave-bar');
        var step = Math.floor(dataArray.length / bars.length);

        bars.forEach(function(bar, i) {
            var value = dataArray[i * step] || 0;
            var height = Math.max(4, (value / 255) * 28);
            bar.style.height = height + 'px';
        });

        waveformAnimation = requestAnimationFrame(animateWaveform);
    }

    function sendVoiceMessage(audioFile) {
        if (!currentChatId) return;

        var formData = new FormData();
        formData.append('file', audioFile);
        var token = document.querySelector('meta[name="csrf-token"]');
        if (token) formData.append('csrf_token', token.content);

        fetch('/api/upload', {
            method: 'POST',
            body: formData,
            credentials: 'same-origin'
        })
        .then(function(r) { return r.json(); })
        .then(function(result) {
            if (result.error) {
                showToast(result.error, 'error');
                return;
            }

            socket.emit('send_message', {
                chat_id: currentChatId,
                text: '',
                file_url: result.file_url,
                file_name: result.file_name,
                file_type: 'audio',
                file_size: result.file_size
            });

            socket.emit('stop_typing', { chat_id: currentChatId });
        });
    }

    var currentPlayingAudio = null;
    var currentPlayingBtn = null;

    function playAudioMessage(btn) {
        var audioUrl = btn.dataset.audioUrl;
        var audioId = btn.dataset.audioId;
        var waveform = document.getElementById(audioId + '-waveform');
        var durationEl = document.getElementById(audioId + '-duration');

        if (currentPlayingAudio && currentPlayingBtn === btn) {
            currentPlayingAudio.pause();
            currentPlayingAudio = null;
            btn.textContent = '▶';
            return;
        }

        if (currentPlayingAudio) {
            currentPlayingAudio.pause();
            currentPlayingAudio = null;
            if (currentPlayingBtn) {
                currentPlayingBtn.textContent = '▶';
            }
        }

        var audio = new Audio(audioUrl);
        currentPlayingAudio = audio;
        currentPlayingBtn = btn;

        btn.textContent = '⏸';

        audio.addEventListener('loadedmetadata', function() {
            var duration = Math.floor(audio.duration);
            var minutes = Math.floor(duration / 60);
            var seconds = duration % 60;
            durationEl.textContent = minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
        });

        audio.addEventListener('timeupdate', function() {
            var progress = audio.currentTime / audio.duration;
            var bars = waveform.querySelectorAll('.audio-wave-bar');
            var playedCount = Math.floor(progress * bars.length);

            bars.forEach(function(bar, i) {
                if (i < playedCount) {
                    bar.classList.add('played');
                } else {
                    bar.classList.remove('played');
                }
            });

            var remaining = Math.floor(audio.duration - audio.currentTime);
            var minutes = Math.floor(remaining / 60);
            var seconds = remaining % 60;
            durationEl.textContent = minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
        });

        audio.addEventListener('ended', function() {
            btn.textContent = '▶';
            currentPlayingAudio = null;
            currentPlayingBtn = null;
            var bars = waveform.querySelectorAll('.audio-wave-bar');
            bars.forEach(function(bar) {
                bar.classList.remove('played');
            });
        });

        audio.play();
    }

    function renderAudioMessage(msg) {
        var audioId = 'audio-' + msg.id;
        var html = '<div class="msg-audio">' +
            '<button class="audio-play-btn" data-audio-id="' + audioId + '" data-audio-url="' + escapeHtml(msg.file_url) + '">▶</button>' +
            '<div class="audio-waveform" id="' + audioId + '-waveform">';

        for (var i = 0; i < 20; i++) {
            var height = Math.random() * 20 + 5;
            html += '<div class="audio-wave-bar" style="height: ' + height + 'px;"></div>';
        }

        html += '</div>' +
            '<div class="audio-duration" id="' + audioId + '-duration">0:00</div>' +
            '</div>';

        return html;
    }

    function initMobileViewport() {
        if (!window.visualViewport) return;

        var messageInput = document.getElementById('message-input');
        var messagesContainer = document.getElementById('messages');
        var viewport = window.visualViewport;
        var initialHeight = viewport.height;
        var keyboardOpen = false;

        function handleViewportResize() {
            if (!messagesContainer) return;

            var heightDiff = initialHeight - viewport.height;
            var isKeyboardOpen = heightDiff > 150;

            if (isKeyboardOpen && !keyboardOpen) {
                keyboardOpen = true;
                messagesContainer.style.scrollBehavior = 'auto';
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            } else if (!isKeyboardOpen && keyboardOpen) {
                keyboardOpen = false;
                messagesContainer.style.scrollBehavior = 'smooth';
            }

            if (keyboardOpen) {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        }

        viewport.addEventListener('resize', handleViewportResize);

        if (messageInput) {
            messageInput.addEventListener('focus', function () {
                setTimeout(function () {
                    if (messagesContainer) {
                        messagesContainer.style.scrollBehavior = 'auto';
                        messagesContainer.scrollTop = messagesContainer.scrollHeight;
                        setTimeout(function () {
                            messagesContainer.style.scrollBehavior = 'smooth';
                        }, 500);
                    }
                }, 100);
            });
        }
    }

    function loadSystemBanner() {
        api('GET', '/auth/api/announcement').then(function(data) {
            if (data && data.is_active) {
                var banner = document.getElementById('system-banner');
                var textEl = document.getElementById('system-banner-text');
                if (banner && textEl) {
                    textEl.textContent = data.text;
                    banner.classList.remove('hidden');
                }
            }
        }).catch(function() {});
    }

    function initSystemBanner() {
        var closeBtn = document.getElementById('system-banner-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                document.getElementById('system-banner').classList.add('hidden');
            });
        }
        loadSystemBanner();
    }

    function initAdminPanel() {
        if (!currentUser.isAdmin) return;

        var sidebarFooter = document.querySelector('.sidebar-footer');
        if (!sidebarFooter) return;

        var adminLink = document.createElement('div');
        adminLink.className = 'admin-link';
        adminLink.innerHTML = '<span>⚙️</span><span>Админ-панель</span>';
        adminLink.addEventListener('click', showAdminPanel);
        sidebarFooter.insertBefore(adminLink, sidebarFooter.firstChild);
    }

    function showAdminPanel() {
        var modal = document.getElementById('modal');
        var title = document.getElementById('modal-title');
        var content = document.getElementById('modal-content');
        var overlay = document.getElementById('modal-overlay');

        title.textContent = 'Админ-панель';
        content.innerHTML =
            '<div class="admin-announcement-form">' +
            '<h4>📢 Системное оповещение</h4>' +
            '<textarea id="announcement-text" placeholder="Текст оповещения для всех пользователей..."></textarea>' +
            '<div class="admin-announcement-actions">' +
            '<button class="admin-btn-delete" id="admin-delete-announcement">Удалить</button>' +
            '<button class="admin-btn-publish" id="admin-publish-announcement">Опубликовать</button>' +
            '</div></div>' +
            '<hr style="border-color:var(--border);margin:20px 0;">' +
            '<h4>👥 Пользователи (<span id="admin-users-count">...</span>)</h4>' +
            '<div id="admin-users-table-wrapper" style="max-height:300px;overflow-y:auto;"></div>';

        overlay.classList.remove('hidden');

        var publishBtn = document.getElementById('admin-publish-announcement');
        var deleteBtn = document.getElementById('admin-delete-announcement');
        var textarea = document.getElementById('announcement-text');

        publishBtn.addEventListener('click', function() {
            var text = textarea.value.trim();
            if (!text) { showToast('Введите текст оповещения', 'error'); return; }
            api('POST', '/auth/api/announcement', { text: text }).then(function(r) {
                if (r.error) { showToast(r.error, 'error'); return; }
                showToast('Оповещение опубликовано!', 'success');
                overlay.classList.add('hidden');
            });
        });

        deleteBtn.addEventListener('click', function() {
            api('DELETE', '/auth/api/announcement').then(function() {
                showToast('Оповещение удалено', 'success');
                overlay.classList.add('hidden');
            });
        });

        api('GET', '/auth/api/admin/users').then(function(users) {
            document.getElementById('admin-users-count').textContent = users.length;
            var html = '<table class="admin-users-table"><thead><tr><th>ID</th><th>Ник</th><th>Email</th><th>Роль</th><th>Был</th><th></th></tr></thead><tbody>';
            users.forEach(function(u) {
                html += '<tr>' +
                    '<td>' + u.id + '</td>' +
                    '<td>' + escapeHtml(u.nickname) + '</td>' +
                    '<td>' + escapeHtml(u.email) + '</td>' +
                    '<td>' + (u.is_admin ? '👑 Админ' : '👤') + '</td>' +
                    '<td>' + escapeHtml(u.last_seen) + '</td>' +
                    '<td><button class="admin-user-delete" data-uid="' + u.id + '" data-name="' + escapeHtml(u.nickname) + '">Удалить</button></td>' +
                    '</tr>';
            });
            html += '</tbody></table>';
            document.getElementById('admin-users-table-wrapper').innerHTML = html;

            document.querySelectorAll('.admin-user-delete').forEach(function(btn) {
                btn.addEventListener('click', function() {
                    var uid = this.dataset.uid;
                    var name = this.dataset.name;
                    showConfirm('Удалить пользователя ' + name + '? Все его чаты и сообщения будут удалены.', function() {
                        api('DELETE', '/auth/api/admin/users/' + uid).then(function(r) {
                            if (r.error) { showToast(r.error, 'error'); return; }
                            showToast('Пользователь удалён', 'success');
                            showAdminPanel();
                        });
                    });
                });
            });
        });
    }

    initSystemBanner();
    initAdminPanel();
    init();
})();