/**
 * @name SkormThemeSync
 * @author Bleaven
 * @description Applies the active SKORM background, animated logo and palette to every connected BetterDiscord client within a few seconds.
 * @version 2.0.0
 * @source https://github.com/Bl3aven/skorm-discord-customization/blob/main/SkormThemeSync.plugin.js
 * @website https://github.com/Bl3aven/skorm-discord-customization
 * @updateUrl https://raw.githubusercontent.com/Bl3aven/skorm-discord-customization/main/SkormThemeSync.plugin.js
 */

"use strict";

const PLUGIN_NAME = "SkormThemeSync";
const POLL_INTERVAL_MS = 3000;
const REQUEST_TIMEOUT_MS = 10000;
const LIVE_BASE = "https://skormdemo.tournayre.ovh/theme-live";
const ACTIVE_STATE_URL = `${LIVE_BASE}/active.json`;
const BACKGROUND_URL = `${LIVE_BASE}/background.png`;
const LOGO_URL = `${LIVE_BASE}/logo.webp`;
const PALETTE_URL = `${LIVE_BASE}/palette.css`;
const RGB_PROPERTIES = [
    "--skorm-base-rgb",
    "--skorm-secondary-rgb",
    "--skorm-accent-rgb"
];

module.exports = class SkormThemeSync {
    constructor() {
        this.api = new BdApi(PLUGIN_NAME);
        this.timer = null;
        this.syncing = false;
        this.lastVersion = "";
        this.lastErrorAt = 0;
    }

    start() {
        this.ensureDynamicThemeEnabled();
        void this.sync(true);
        this.timer = setInterval(() => void this.sync(false), POLL_INTERVAL_MS);
    }

    stop() {
        if (this.timer) clearInterval(this.timer);
        this.timer = null;
        for (const property of [
            "--skorm-image",
            "--skorm-server-icon",
            ...RGB_PROPERTIES
        ]) {
            document.documentElement.style.removeProperty(property);
        }
    }

    ensureDynamicThemeEnabled() {
        for (const themeName of ["SkormDynamic", "TropicalSkorm"]) {
            if (!BdApi.Themes.get(themeName)) continue;
            BdApi.Themes.enable(themeName);
            return;
        }
        this.api.UI.showToast(
            "Installe aussi SkormDynamic.theme.css pour afficher le thème SKORM.",
            {type: "warning", timeout: 8000}
        );
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

    async sync(initial) {
        if (this.syncing) return;
        this.syncing = true;
        try {
            const state = JSON.parse(await this.fetchText(ACTIVE_STATE_URL));
            const slug = String(state.slug || "").trim().toLowerCase();
            const selectedAt = String(state.selected_at || "").trim();
            if (!/^[a-z0-9][a-z0-9-]{0,63}$/.test(slug) || !selectedAt) {
                throw new Error("État de thème Nextcloud invalide");
            }

            const version = `${slug}:${selectedAt}`;
            if (!initial && version === this.lastVersion) return;

            const palette = this.parsePalette(await this.fetchText(PALETTE_URL));
            const cacheKey = encodeURIComponent(version);
            const rootStyle = document.documentElement.style;
            rootStyle.setProperty(
                "--skorm-image",
                `url("${BACKGROUND_URL}?v=${cacheKey}")`
            );
            rootStyle.setProperty(
                "--skorm-server-icon",
                `url("${LOGO_URL}?v=${cacheKey}")`
            );
            for (const [property, value] of Object.entries(palette)) {
                rootStyle.setProperty(property, value);
            }

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
