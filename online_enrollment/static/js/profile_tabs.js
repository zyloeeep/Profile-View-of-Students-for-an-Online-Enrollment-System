document.addEventListener('DOMContentLoaded', function () {
    var tabs = document.querySelectorAll('[data-tab]');
    var panels = document.querySelectorAll('#tab-panels > section');

    if (tabs.length === 0) {
        return;
    }

    function showTab(name) {
        tabs.forEach(function (tab) {
            tab.setAttribute('aria-selected', tab.dataset.tab === name ? 'true' : 'false');
        });
        panels.forEach(function (panel) {
            panel.hidden = panel.id !== name;
        });
    }

    tabs.forEach(function (tab) {
        tab.addEventListener('click', function () {
            showTab(tab.dataset.tab);
        });
    });

    showTab('personal');
});