/**
 * @name SkormThemeSync
 * @author Bleaven
 * @description Applies the active SKORM visuals only inside the SKORM guild while keeping its animated server icon visible everywhere.
 * @version 2.2.0
 * @source https://github.com/Bl3aven/skorm-discord-customization/blob/main/SkormThemeSync.plugin.js
 * @website https://github.com/Bl3aven/skorm-discord-customization
 * @updateUrl https://raw.githubusercontent.com/Bl3aven/skorm-discord-customization/main/SkormThemeSync.plugin.js
 */

"use strict";

const PLUGIN_NAME = "SkormThemeSync";
const SKORM_GUILD_ID = "1523407172514349097";
const ACTIVE_CLASS = "skorm-active";
const POLL_INTERVAL_MS = 3000;
const SCOPE_INTERVAL_MS = 250;
const REQUEST_TIMEOUT_MS = 10000;
const LIVE_BASE = "https://skormdemo.tournayre.ovh/theme-live";
const ACTIVE_STATE_URL = `${LIVE_BASE}/active.json`;
const LOGO_URL = `${LIVE_BASE}/logo.webp`;
const PALETTE_URL = `${LIVE_BASE}/palette.css`;
const STYLE_ID = "skorm-theme-sync-live-values";
const RGB_PROPERTIES = [
    "--skorm-base-rgb",
    "--skorm-secondary-rgb",
    "--skorm-accent-rgb"
];

module.exports = class SkormThemeSync {
    constructor() {
        this.api = new BdApi(PLUGIN_NAME);
        this.timer = null;
        this.scopeTimer = null;
        this.themeCheckTimer = null;
        this.syncing = false;
        this.lastVersion = "";
        this.lastErrorAt = 0;
    }

    start() {
        this.updateScope();
        this.scopeTimer = setInterval(
            () => this.updateScope(),
            SCOPE_INTERVAL_MS
        );
        if (!this.enableDynamicTheme()) {
            // BetterDiscord can start plugins before it has finished indexing
            // themes. Retry once after startup before showing a warning.
            this.themeCheckTimer = setTimeout(() => {
                this.themeCheckTimer = null;
                if (!this.enableDynamicTheme()) {
                    this.api.UI.showToast(
                        "Installe aussi SkormDynamic.theme.css pour afficher le thème SKORM.",
                        {type: "warning", timeout: 8000}
                    );
                }
            }, 2000);
        }
        void this.sync(true);
        this.timer = setInterval(() => void this.sync(false), POLL_INTERVAL_MS);
    }

    stop() {
        if (this.timer) clearInterval(this.timer);
        if (this.scopeTimer) clearInterval(this.scopeTimer);
        if (this.themeCheckTimer) clearTimeout(this.themeCheckTimer);
        this.timer = null;
        this.scopeTimer = null;
        this.themeCheckTimer = null;
        document.documentElement.classList.remove(ACTIVE_CLASS);
        document.getElementById(STYLE_ID)?.remove();
    }

    isSkormRoute(pathname = window.location.pathname) {
        const match = /^\/channels\/([^/?#]+)/.exec(pathname);
        return match?.[1] === SKORM_GUILD_ID;
    }

    updateScope(pathname = window.location.pathname) {
        document.documentElement.classList.toggle(
            ACTIVE_CLASS,
            this.isSkormRoute(pathname)
        );
    }

    enableDynamicTheme() {
        for (const themeName of ["SkormDynamic", "TropicalSkorm"]) {
            if (!BdApi.Themes.get(themeName)) continue;
            BdApi.Themes.enable(themeName);
            return true;
        }
        return false;
    }

    async fetchText(url) {
        const separator = url.includes("?") ? "&" : "?";
        const response = await this.api.Net.fetch(
            `${url}${separator}_skorm=${Date.now()}`,
            {
                method: "GET",
                headers: {
                    "Cache-Control": "no-cache, no-store",
                    "Pragma": "no-cache"
                },
                timeout: REQUEST_TIMEOUT_MS
            }
        );
        if (response.status < 200 || response.status >= 300) {
            throw new Error(`HTTP ${response.status} pour ${url}`);
        }
        return response.text();
    }

    parsePalette(css) {
        const palette = {};
        for (const property of RGB_PROPERTIES) {
            const escaped = property.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
            const match = css.match(
                new RegExp(`${escaped}\\s*:\\s*(\\d{1,3})\\s+(\\d{1,3})\\s+(\\d{1,3})\\s*;`)
            );
            if (!match) throw new Error(`Palette invalide: ${property} absent`);
            const channels = match.slice(1).map(Number);
            if (channels.some((channel) => channel < 0 || channel > 255)) {
                throw new Error(`Palette invalide: ${property} hors limites`);
            }
            palette[property] = channels.join(" ");
        }
        return palette;
    }

    applyThemeStyle(cacheKey, palette, backgroundFile) {
        let style = document.getElementById(STYLE_ID);
        if (!style) {
            style = document.createElement("style");
            style.id = STYLE_ID;
            style.dataset.skormThemeSync = "live";
            document.head.append(style);
        }
        const declarations = [
            `--skorm-image: url("${LIVE_BASE}/${backgroundFile}?v=${cacheKey}") !important`,
            `--skorm-server-icon: url("${LOGO_URL}?v=${cacheKey}") !important`,
            ...RGB_PROPERTIES.map(
                (property) => `${property}: ${palette[property]} !important`
            )
        ];
        style.textContent = `:root {\n    ${declarations.join(";\n    ")};\n}`;
    }

    async sync(initial) {
        if (this.syncing) return;
        this.syncing = true;
        try {
            const state = JSON.parse(await this.fetchText(ACTIVE_STATE_URL));
            const slug = String(state.slug || "").trim().toLowerCase();
            const selectedAt = String(state.selected_at || "").trim();
            const backgroundFile = String(
                state.background || "background.png"
            ).trim().toLowerCase();
            if (!/^[a-z0-9][a-z0-9-]{0,63}$/.test(slug) || !selectedAt) {
                throw new Error("État de thème Nextcloud invalide");
            }
            if (!/^background\.(?:png|webp)$/.test(backgroundFile)) {
                throw new Error("Nom de fond live invalide");
            }

            const version = `${slug}:${backgroundFile}:${selectedAt}`;
            if (!initial && version === this.lastVersion) return;

            const palette = this.parsePalette(await this.fetchText(PALETTE_URL));
            const cacheKey = encodeURIComponent(version);
            this.applyThemeStyle(cacheKey, palette, backgroundFile);

            const changed = this.lastVersion && this.lastVersion !== version;
            this.lastVersion = version;
            if (initial || changed) {
                this.api.UI.showToast(
                    `Thème SKORM synchronisé : ${state.name || slug}`,
                    {type: "success", timeout: 4000}
                );
            }
        }
        catch (error) {
            const now = Date.now();
            if (now - this.lastErrorAt > 60000) {
                this.api.Logger.error("Synchronisation impossible", error);
                this.api.UI.showToast(
                    "Synchronisation SKORM temporairement indisponible.",
                    {type: "error", timeout: 5000}
                );
                this.lastErrorAt = now;
            }
        }
        finally {
            this.syncing = false;
        }
    }
};
