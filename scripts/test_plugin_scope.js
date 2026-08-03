"use strict";

const assert = require("node:assert/strict");
const Plugin = require("../SkormThemeSync.plugin.js");

const plugin = Object.create(Plugin.prototype);

assert.equal(
    plugin.isSkormRoute("/channels/1523407172514349097/1523407173210738791"),
    true,
    "SKORM channels must activate the theme"
);
assert.equal(
    plugin.isSkormRoute("/channels/123456789012345678/987654321098765432"),
    false,
    "another guild must keep Discord's regular theme"
);
assert.equal(
    plugin.isSkormRoute("/channels/@me/123456789012345678"),
    false,
    "direct messages must keep Discord's regular theme"
);
assert.equal(
    plugin.isSkormRoute("/shop"),
    false,
    "non-channel pages must keep Discord's regular theme"
);

console.log("SKORM route scoping validated.");
