# Copyright NGGT.LightKeeper. All Rights Reserved.

from django.contrib import admin

from Apps.Data.models import Chat, Message, MessageImage, OllamaPreset, Workspace


# Register workspace records in the admin.
@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ("name", "path", "created_at", "updated_at")
    search_fields = ("name", "path")


# Register chat records in the admin.
@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("title", "workspace", "active_tool_slug", "created_at", "updated_at")
    search_fields = ("title", "active_tool_slug")
    list_filter = ("workspace",)


# Register chat messages in the admin.
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("chat", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("content",)


# Register legacy stored images in the admin.
@admin.register(MessageImage)
class MessageImageAdmin(admin.ModelAdmin):
    list_display = ("message", "mime_type", "order")
    list_filter = ("mime_type",)


# Register Ollama presets in the admin.
@admin.register(OllamaPreset)
class OllamaPresetAdmin(admin.ModelAdmin):
    list_display = ("model_name", "name", "is_default", "is_active", "updated_at")
    list_filter = ("is_default", "is_active")
    search_fields = ("model_name", "name")
