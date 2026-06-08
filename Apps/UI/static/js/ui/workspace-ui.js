// Copyright NGGT.LightKeeper. All Rights Reserved.

import { deleteJson, postJson } from '../main/api.js';
import { escHtml, escapeAttributeValue, parseJsonScript } from '../main/utils.js';
import { t } from '../main/i18n.js';

const WORKSPACE_STORAGE_KEY = 'aslm.currentWorkspaceId';

// Workspace UI.
// Composer workspace picker and grouped sidebar helpers.
export function createWorkspaceUi(context) {
  const { dom, icons, state } = context;
  let chatController = null;
  let activeWorkspaceMenuTarget = null;
  let activeWorkspaceMenuId = null;

  state.workspaces = parseJsonScript('workspacesData') || [];

  function workspaceUrl(workspaceId) {
    return workspaceId ? `/workspace/${workspaceId}/` : '/';
  }

  function workspaceChatUrl(workspaceId, chatId) {
    if (!workspaceId) {
      return '/';
    }
    if (!chatId) {
      return workspaceUrl(workspaceId);
    }
    return `/workspace/${workspaceId}/chat/${chatId}/`;
  }

  function compareWorkspaceNames(a, b) {
    return (a.name || '').localeCompare(b.name || '', undefined, { sensitivity: 'base' });
  }

  function sortedWorkspaces() {
    return [...(state.workspaces || [])].sort(compareWorkspaceNames);
  }

  function rememberWorkspace(workspaceId) {
    if (!workspaceId) {
      return;
    }
    try {
      window.localStorage.setItem(WORKSPACE_STORAGE_KEY, workspaceId);
    } catch (_error) {
      // Ignore storage failures in privacy-restricted contexts.
    }
  }

  function clearRememberedWorkspace() {
    try {
      window.localStorage.removeItem(WORKSPACE_STORAGE_KEY);
    } catch (_error) {
      // Ignore storage failures in privacy-restricted contexts.
    }
  }

  function readRememberedWorkspace() {
    try {
      return window.localStorage.getItem(WORKSPACE_STORAGE_KEY) || '';
    } catch (_error) {
      return '';
    }
  }

  function getWorkspaceById(workspaceId) {
    return (state.workspaces || []).find(function match(workspace) {
      return String(workspace.id) === String(workspaceId);
    }) || null;
  }

  function updateWorkspaceChipLabel() {
    const workspace = getWorkspaceById(state.currentWorkspaceId);
    const label = workspace
      ? workspace.name
      : t('workspace.select', {}, 'Select workspace');
    dom.$workspacePickerLabel.text(label);
  }

  function closeWorkspaceActionMenu() {
    if (activeWorkspaceMenuTarget) {
      activeWorkspaceMenuTarget.removeClass('is-open');
    }
    dom.$workspaceItemDropdown.hide();
    activeWorkspaceMenuTarget = null;
    activeWorkspaceMenuId = null;
  }

  function openWorkspaceActionMenu($btn, workspaceId) {
    closeWorkspaceActionMenu();
    activeWorkspaceMenuTarget = $btn;
    activeWorkspaceMenuId = workspaceId;
    $btn.addClass('is-open');

    dom.$workspaceItemDropdown.show();
    const rect = $btn[0].getBoundingClientRect();
    const menuWidth = dom.$workspaceItemDropdown.outerWidth();
    dom.$workspaceItemDropdown.css({
      top: rect.bottom + window.scrollY + 2,
      left: rect.right + window.scrollX - menuWidth
    });
  }

  function closeWorkspacePickerMenu() {
    closeWorkspaceActionMenu();
    dom.$workspacePickerMenu.hide();
    dom.$workspacePickerBtn.removeClass('is-open').attr('aria-expanded', 'false');
  }

  function renderWorkspacePickerMenu() {
    closeWorkspaceActionMenu();
    const $list = dom.$workspacePickerList.empty();
    const workspaces = sortedWorkspaces();

    if (!workspaces.length) {
      $list.append(
        `<div class="composer-workspace-menu-empty">${escHtml(t('workspace.noneYet', {}, 'No workspaces yet'))}</div>`
      );
      return;
    }

    const optionsLabel = escHtml(t('workspace.options', {}, 'Workspace options'));
    workspaces.forEach(function appendWorkspace(workspace) {
      const isActive = String(workspace.id) === String(state.currentWorkspaceId);
      const $row = $(`
        <div class="composer-workspace-menu-row">
          <button type="button" class="composer-workspace-menu-item${isActive ? ' is-active' : ''}"
                  data-workspace-id="${escapeAttributeValue(workspace.id)}" role="menuitem">
            <span>${escHtml(workspace.name || '')}</span>
            <span class="composer-workspace-menu-item-path">${escHtml(workspace.path || '')}</span>
          </button>
          <button type="button" class="composer-workspace-menu-more"
                  data-workspace-id="${escapeAttributeValue(workspace.id)}"
                  aria-label="${optionsLabel}" title="${optionsLabel}">
            ${icons.WORKSPACE_MORE_ICON}
          </button>
        </div>
      `);
      $list.append($row);
    });
  }

  function insertSidebarGroupAlphabetically($group, workspaceName) {
    const nameKey = (workspaceName || '').toLocaleLowerCase();
    let inserted = false;

    dom.$historyList.find('.history-workspace-group').each(function compareGroups() {
      const otherName = $(this).find('.history-workspace-name').text().toLocaleLowerCase();
      if (nameKey < otherName) {
        $(this).before($group);
        inserted = true;
        return false;
      }
    });

    if (!inserted) {
      dom.$historyList.append($group);
    }
  }

  function ensureSidebarWorkspaceGroup(workspace) {
    let $group = dom.$historyList.find(`.history-workspace-group[data-workspace-id="${workspace.id}"]`);
    if ($group.length) {
      return $group;
    }

    dom.$historyList.find('.empty-state').remove();

    $group = $(`
      <section class="history-workspace-group" data-workspace-id="${escapeAttributeValue(workspace.id)}">
        <div class="history-workspace-header">
          <span class="history-workspace-name">${escHtml(workspace.name || '')}</span>
        </div>
        <div class="history-workspace-chats"></div>
      </section>
    `);
    insertSidebarGroupAlphabetically($group, workspace.name);
    return $group;
  }

  function removeSidebarWorkspaceGroup(workspaceId) {
    dom.$historyList.find(`.history-workspace-group[data-workspace-id="${workspaceId}"]`).remove();
    if (!dom.$historyList.find('.history-workspace-group').length) {
      dom.$historyList.append(
        `<div class="chat-item empty-state"><span class="chat-item-title">${escHtml(t('workspace.noneYet', {}, 'No workspaces yet'))}</span></div>`
      );
    }
  }

  function syncComposerWorkspaceBar() {
    const showBar = dom.$welcomeScreen.is(':visible');
    dom.$composerWorkspaceBar.toggle(showBar);
    updateWorkspaceChipLabel();
    dom.$newChatBtn.attr('href', state.currentWorkspaceId ? workspaceUrl(state.currentWorkspaceId) : '/');
  }

  function syncWorkspaceUi() {
    updateWorkspaceChipLabel();
    renderWorkspacePickerMenu();
    dom.$newChatBtn.attr('href', state.currentWorkspaceId ? workspaceUrl(state.currentWorkspaceId) : '/');
    syncComposerWorkspaceBar();
  }

  function selectWorkspace(workspaceId, options) {
    const opts = options || {};
    const cleaned = String(workspaceId || '').trim();
    if (!cleaned) {
      state.currentWorkspaceId = null;
      syncWorkspaceUi();
      return;
    }

    state.currentWorkspaceId = cleaned;
    rememberWorkspace(cleaned);
    syncWorkspaceUi();

    if (opts.startNewChat && chatController) {
      chatController.startNewChat({ pushState: opts.pushState !== false });
    }
  }

  function setChatController(controller) {
    chatController = controller;
  }

  async function deleteWorkspace(workspaceId) {
    const workspace = getWorkspaceById(workspaceId);
    const title = workspace ? workspace.name : '';
    if (!window.confirm(t('workspace.deleteConfirm', { title }, 'Delete workspace?'))) {
      return;
    }

    try {
      const response = await deleteJson(`/api/workspaces/${workspaceId}/delete/`);
      if (!response || !response.ok) {
        throw new Error(response && response.error ? response.error : 'Delete failed');
      }
    } catch (error) {
      console.error('Failed to delete workspace:', error);
      window.alert(String(error && error.message ? error.message : error));
      return;
    }

    state.workspaces = (state.workspaces || []).filter(function keepWorkspace(workspace) {
      return String(workspace.id) !== String(workspaceId);
    });
    removeSidebarWorkspaceGroup(workspaceId);

    if (String(state.currentWorkspaceId) === String(workspaceId)) {
      state.currentWorkspaceId = null;
      clearRememberedWorkspace();
      if (chatController) {
        chatController.startNewChat({ pushState: false });
      }
      window.history.pushState({}, document.title, '/');
    }

    syncWorkspaceUi();
  }

  async function createWorkspace() {
    if (state.workspaceCreateInFlight) {
      return null;
    }

    closeWorkspacePickerMenu();
    state.workspaceCreateInFlight = true;
    try {
      const response = await postJson('/api/workspaces/create/', {
        title: t('workspace.pickerTitle', {}, 'Select workspace folder')
      });

      if (response.cancelled) {
        return null;
      }

      const workspace = response.workspace;
      if (!workspace || !workspace.id) {
        throw new Error(response.error || 'Workspace creation failed');
      }

      if (!getWorkspaceById(workspace.id)) {
        state.workspaces = [...(state.workspaces || []), workspace].sort(compareWorkspaceNames);
      }

      selectWorkspace(workspace.id, { startNewChat: true, pushState: true });
      window.history.pushState(
        { workspaceId: workspace.id },
        workspace.name || t('meta.appTitle', {}, 'ASLM Chat'),
        workspaceUrl(workspace.id)
      );
      return workspace;
    } finally {
      state.workspaceCreateInFlight = false;
    }
  }

  function bindEvents() {
    dom.$workspacePickerBtn.on('click', function onPickerClick(event) {
      event.preventDefault();
      event.stopPropagation();
      const isOpen = dom.$workspacePickerMenu.is(':visible');
      if (isOpen) {
        closeWorkspacePickerMenu();
        return;
      }
      renderWorkspacePickerMenu();
      dom.$workspacePickerMenu.show();
      dom.$workspacePickerBtn.addClass('is-open').attr('aria-expanded', 'true');
    });

    dom.$newWorkspaceBtn.on('click', function onCreateWorkspaceClick(event) {
      event.preventDefault();
      createWorkspace().catch(function onCreateWorkspaceError(error) {
        console.error('Failed to create workspace:', error);
        window.alert(String(error && error.message ? error.message : error));
      });
    });

    dom.$workspacePickerList.on('click', '.composer-workspace-menu-item', function onWorkspacePick(event) {
      event.preventDefault();
      const workspaceId = $(this).data('workspace-id');
      closeWorkspacePickerMenu();
      selectWorkspace(workspaceId, { startNewChat: true, pushState: true });
      const workspace = getWorkspaceById(workspaceId);
      window.history.pushState(
        { workspaceId },
        workspace && workspace.name ? workspace.name : t('meta.appTitle', {}, 'ASLM Chat'),
        workspaceUrl(workspaceId)
      );
    });

    dom.$workspacePickerList.on('click', '.composer-workspace-menu-more', function onWorkspaceMoreClick(event) {
      event.preventDefault();
      event.stopPropagation();
      const $btn = $(this);
      const workspaceId = $btn.data('workspace-id');
      if (activeWorkspaceMenuTarget && activeWorkspaceMenuTarget.is($btn)) {
        closeWorkspaceActionMenu();
        return;
      }
      openWorkspaceActionMenu($btn, workspaceId);
    });

    dom.$workspaceDeleteBtn.on('click', function onWorkspaceDeleteClick(event) {
      event.preventDefault();
      event.stopPropagation();
      const workspaceId = activeWorkspaceMenuId;
      closeWorkspaceActionMenu();
      closeWorkspacePickerMenu();
      if (!workspaceId) {
        return;
      }
      deleteWorkspace(workspaceId).catch(function onDeleteWorkspaceError(error) {
        console.error('Failed to delete workspace:', error);
        window.alert(String(error && error.message ? error.message : error));
      });
    });

    $(document).on('click', function onDocumentClick(event) {
      const $target = $(event.target);
      if (!$target.closest('.composer-workspace-picker').length) {
        closeWorkspacePickerMenu();
      } else if (!$target.closest('#workspaceItemDropdown, .composer-workspace-menu-more').length) {
        closeWorkspaceActionMenu();
      }
    });
  }

  return {
    bindEvents,
    closeWorkspacePickerMenu,
    createWorkspace,
    ensureSidebarWorkspaceGroup,
    readRememberedWorkspace,
    removeSidebarWorkspaceGroup,
    selectWorkspace,
    setChatController,
    syncComposerWorkspaceBar,
    syncWorkspaceUi,
    workspaceChatUrl,
    workspaceUrl
  };
}
