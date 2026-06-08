// Copyright NGGT.LightKeeper. All Rights Reserved.

import { escHtml, escapeAttributeValue } from '../main/utils.js';
import { t } from '../main/i18n.js';

// Chat history UI.
// Create helpers for the sidebar chat list and menu.
export function createChatHistoryUi(context, dependencies) {
  const { workspaceUi } = dependencies;
  const { dom, icons, state } = context;

  function buildChatItemHtml(chatId, workspaceId, title, dateStr, active) {
    const activeAttr = active ? ' class="chat-item active" aria-current="page"' : ' class="chat-item"';
    const href = workspaceUi.workspaceChatUrl(workspaceId, chatId);

    return `
      <a${activeAttr} href="${escapeAttributeValue(href)}"
         data-chat-id="${escapeAttributeValue(chatId)}"
         data-workspace-id="${escapeAttributeValue(workspaceId)}">
        <div class="chat-item-icon">
          ${icons.CHAT_ITEM_ICON}
        </div>
        <div class="chat-item-body">
          <span class="chat-item-title">${escHtml(title)}</span>
          <span class="chat-item-date">${escHtml(dateStr)}</span>
        </div>
        <button class="chat-item-menu-btn" aria-label="${escHtml(t('sidebar.chatOptions', {}, 'Chat options'))}">
          ${icons.CHAT_ITEM_MENU_ICON}
        </button>
      </a>
    `;
  }

  function chatGroupForWorkspace(workspaceId) {
    const cleaned = String(workspaceId || state.currentWorkspaceId || '').trim();
    if (!cleaned) {
      return $();
    }
    return dom.$historyList.find(`.history-workspace-group[data-workspace-id="${cleaned}"] .history-workspace-chats`);
  }

  function setActiveChat(chatId) {
    dom.$historyList.find('.chat-item').removeClass('active').removeAttr('aria-current');

    if (!chatId) {
      return;
    }

    dom.$historyList
      .find(`.chat-item[data-chat-id="${chatId}"]`)
      .addClass('active')
      .attr('aria-current', 'page');
  }

  function clearActiveChat() {
    setActiveChat('');
  }

  function prependChatItem(chatId, title, dateStr, workspaceId) {
    const wsId = String(workspaceId || state.currentWorkspaceId || '').trim();
    let $chats = chatGroupForWorkspace(wsId);
    if (!$chats.length) {
      const workspace = (state.workspaces || []).find(function match(item) {
        return String(item.id) === wsId;
      });
      if (!workspace) {
        return null;
      }
      workspaceUi.ensureSidebarWorkspaceGroup(workspace);
      $chats = chatGroupForWorkspace(wsId);
      if (!$chats.length) {
        return null;
      }
    }

    setActiveChat('');

    const $newItem = $(buildChatItemHtml(chatId, wsId, title, dateStr, true));
    $chats.prepend($newItem);
    return $newItem;
  }

  function removeChatItem(chatId) {
    const $item = dom.$historyList.find(`.chat-item[data-chat-id="${chatId}"]`);
    const $group = $item.closest('.history-workspace-group');
    $item.remove();

    if ($group.length && !$group.find('.chat-item').length) {
      $group.remove();
      ensureEmptyState();
    }
  }

  function ensureEmptyState() {
    if (dom.$historyList.find('.chat-item:not(.empty-state)').length > 0) {
      return;
    }

    if (!dom.$historyList.find('.history-workspace-group').length) {
      dom.$historyList.append(
        `<div class="chat-item empty-state"><span class="chat-item-title">${escHtml(t('workspace.noneYet', {}, 'No workspaces yet'))}</span></div>`
      );
    }
  }

  function openChatMenu($item, event) {
    event.preventDefault();
    event.stopPropagation();

    state.activeMenuTarget = $item;

    const rect = $item[0].getBoundingClientRect();
    dom.$chatItemDropdown.css({
      top: rect.bottom + window.scrollY + 2,
      left: rect.left + window.scrollX,
      minWidth: rect.width
    }).show();
  }

  function closeChatMenu() {
    dom.$chatItemDropdown.hide();
    state.activeMenuTarget = null;
  }

  function toggleChatMenu($item, event) {
    if (state.activeMenuTarget && state.activeMenuTarget.is($item)) {
      closeChatMenu();
      return;
    }

    openChatMenu($item, event);
  }

  function getActiveMenuTarget() {
    return state.activeMenuTarget;
  }

  return {
    buildChatItemHtml,
    clearActiveChat,
    closeChatMenu,
    ensureEmptyState,
    getActiveMenuTarget,
    openChatMenu,
    prependChatItem,
    removeChatItem,
    setActiveChat,
    toggleChatMenu
  };
}
