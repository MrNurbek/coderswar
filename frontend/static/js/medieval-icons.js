/**
 * medieval-icons.js
 * Emoji → RPG Awesome icon library (o'rta asr stilistikasi)
 * Barcha text nodelarni, shu jumladan dinamik kontent ham, almashtiradi.
 */
(function () {
  'use strict';

  // [emoji, 'ra-icon-name']  —  uzunroqlar avval (variation selector uchun)
  const MAP = [
    // Navigation / UI
    ['📊', 'ra-compass'],
    ['📚', 'ra-scroll'],
    ['💻', 'ra-anvil'],
    ['📈', 'ra-compass'],
    ['🔍', 'ra-eye'],
    ['🏰', 'ra-castle'],
    ['⚡', 'ra-lightning'],
    ['🏆', 'ra-trophy'],
    ['👤', 'ra-player'],
    ['👥', 'ra-player'],
    ['⚙️', 'ra-cog'],
    ['⚙',  'ra-cog'],
    ['🔔', 'ra-torch'],
    ['👁️', 'ra-eye'],
    ['👁',  'ra-eye'],
    ['✍️', 'ra-scroll'],
    ['✍',  'ra-scroll'],
    ['🎬', 'ra-eye'],
    ['📝', 'ra-diploma'],
    ['📋', 'ra-scroll'],
    ['📄', 'ra-scroll'],
    ['📁', 'ra-scroll'],
    // Combat / Characters
    ['⚔️', 'ra-crossed-swords'],
    ['⚔',  'ra-crossed-swords'],
    ['🏹', 'ra-bow-arrow'],
    ['🛡️', 'ra-shield'],
    ['🛡',  'ra-shield'],
    ['🪄', 'ra-fairy-wand'],
    ['⚜️', 'ra-crown'],
    ['⚜',  'ra-crown'],
    ['👑', 'ra-crown'],
    ['🗡️', 'ra-sword'],
    ['🗡',  'ra-sword'],
    ['💪', 'ra-crossed-swords'],
    // Equipment
    ['⛑️', 'ra-helmet'],
    ['⛑',  'ra-helmet'],
    ['🪖', 'ra-knight-helm'],
    ['💍', 'ra-ring'],
    ['👟', 'ra-boots'],
    ['🥾', 'ra-boots'],
    ['🪵', 'ra-round-shield'],
    ['⚜️', 'ra-crown'],
    // Stars / Magic
    ['⭐', 'ra-star'],
    ['🌟', 'ra-star'],
    ['✨', 'ra-magic-swirl'],
    ['🔮', 'ra-crystal-ball'],
    ['🧠', 'ra-crystal-ball'],
    ['🤖', 'ra-crystal-ball'],
    ['💡', 'ra-torch'],
    ['💡', 'ra-torch'],
    // Fire / Elements
    ['🔥', 'ra-fire'],
    ['🌱', 'ra-campfire'],
    ['🚀', 'ra-lightning'],
    ['🎉', 'ra-fire'],
    ['🎆', 'ra-fireball'],
    // Targets & Achievements
    ['🎯', 'ra-archery-target'],
    ['🏅', 'ra-medal'],
    ['🎖️', 'ra-medal'],
    ['🎖',  'ra-medal'],
    ['🥇', 'ra-trophy'],
    ['🥈', 'ra-trophy'],
    ['🥉', 'ra-trophy'],
    // Characters / Heroes
    ['🦸', 'ra-knight-helm'],
    ['🦅', 'ra-eagle'],
    ['👨‍🏫', 'ra-hood'],
    ['🎓', 'ra-diploma'],
    ['🧪', 'ra-potion'],
    ['🎮', 'ra-perspective-dice-six'],
    ['🎁', 'ra-gem'],
    ['💎', 'ra-gem'],
    ['💰', 'ra-gold-bar'],
    ['🪙', 'ra-coins'],
    // Status
    ['⏳', 'ra-hourglass'],
    ['⏱️', 'ra-hourglass'],
    ['⏱',  'ra-hourglass'],
    ['🔒', 'ra-lock'],
    ['🔐', 'ra-lock'],
    ['🔓', 'ra-key'],
    ['🔑', 'ra-key'],
    // Edit actions
    ['✏️', 'ra-scroll'],
    ['✏',  'ra-scroll'],
    ['🗑️', 'ra-skull'],
    ['🗑',  'ra-skull'],
    ['💾', 'ra-anvil'],
    ['➕', 'ra-sword'],
    // Communication
    ['💬', 'ra-scroll'],
    ['📧', 'ra-scroll'],
    ['📨', 'ra-scroll'],
    ['📢', 'ra-torch'],
    ['📣', 'ra-torch'],
    ['📤', 'ra-scroll'],
    ['📥', 'ra-scroll'],
    ['📬', 'ra-scroll'],
    ['🔗', 'ra-key'],
    ['📞', 'ra-scroll'],
    ['📲', 'ra-scroll'],
    // Nature / Time
    ['🌙', 'ra-moon'],
    ['☀️', 'ra-sun'],
    ['☀',  'ra-sun'],
    ['🌤️', 'ra-sun'],
    ['📅', 'ra-compass'],
    ['🗓️', 'ra-compass'],
    ['📐', 'ra-compass'],
    // Places / Social
    ['🏫', 'ra-castle'],
    ['🖥️', 'ra-castle'],
    ['🖥',  'ra-castle'],
    ['🌍', 'ra-compass'],
    ['🎪', 'ra-castle'],
    ['🏟️', 'ra-castle'],
    // Misc
    ['👋', 'ra-sword'],
    ['😤', 'ra-skull'],
    ['😊', 'ra-crown'],
    ['🆕', 'ra-star'],
    ['💚', 'ra-health'],
    ['🚨', 'ra-fire'],
    ['🚫', 'ra-skull'],
    ['🧮', 'ra-coins'],
    ['📐', 'ra-compass'],
    ['🎭', 'ra-player'],
    ['🎲', 'ra-perspective-dice-six'],
  ];

  // Uzunroqdan qisqaga tartiblash (multi-codepoint emoji birinchi)
  const SORTED = [...MAP].sort((a, b) => b[0].length - a[0].length);

  const SKIP = new Set(['SCRIPT', 'STYLE', 'INPUT', 'TEXTAREA', 'CODE', 'PRE', 'NOSCRIPT']);

  function processTextNode(node) {
    const text = node.textContent;
    // Tez tekshiruv: birorta emoji bormi?
    let anyMatch = false;
    for (const [emoji] of SORTED) {
      if (text.includes(emoji)) { anyMatch = true; break; }
    }
    if (!anyMatch) return;

    // HTML escape, keyin iconlarga almashtirish
    let html = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    let changed = false;
    for (const [emoji, cls] of SORTED) {
      if (html.includes(emoji)) {
        html = html.split(emoji).join(`<i class="ra ${cls}" aria-hidden="true"></i>`);
        changed = true;
      }
    }

    if (!changed) return;

    const tpl = document.createElement('template');
    tpl.innerHTML = html;
    node.parentNode.replaceChild(tpl.content, node);
  }

  function walkTree(root) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        let p = node.parentNode;
        while (p) {
          if (SKIP.has(p.nodeName)) return NodeFilter.FILTER_REJECT;
          p = p.parentNode;
        }
        return NodeFilter.FILTER_ACCEPT;
      },
    });
    const nodes = [];
    let n;
    while ((n = walker.nextNode())) nodes.push(n);
    nodes.forEach(processTextNode);
  }

  function init() {
    walkTree(document.body);

    // Dinamik kontent uchun (API javoblari, JS innerHTML)
    const obs = new MutationObserver(mutations => {
      for (const m of mutations) {
        for (const node of m.addedNodes) {
          if (node.nodeType === 1) walkTree(node);
          else if (node.nodeType === 3) processTextNode(node);
        }
      }
    });
    obs.observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
