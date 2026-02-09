// 价格脉动 - 网页按钮修复脚本
// 在浏览器控制台运行此脚本即可修复

(function() {
    console.log('=== 开始修复价格脉动按钮 ===');

    // 修复1：Hero区域"开始使用"按钮
    const heroStartButton = document.querySelector('.gradient-bg');
    if (heroStartButton && heroStartButton.textContent.includes('开始使用')) {
        heroStartButton.setAttribute('href', 'register.html');
        heroStartButton.addEventListener('click', (e) => {
            e.preventDefault();
            window.location.href = 'register.html';
        });
        console.log('✅ Hero "开始使用" 已修复');
    }

    // 修复2：导航栏"立即试用"按钮
    const navButton = document.querySelector('nav button');
    if (navButton && navButton.textContent.includes('试用')) {
        navButton.setAttribute('onclick', "window.location.href='register.html'");
        navButton.addEventListener('click', () => {
            window.location.href = 'register.html';
        });
        console.log('✅ 导航栏"立即试用" 已修复');
    }

    // 修复3：所有卡片中的"开始使用"按钮
    const cardButtons = document.querySelectorAll('button');
    cardButtons.forEach((button, index) => {
        const text = button.textContent.trim();
        if (text.includes('开始使用') || text.includes('订阅')) {
            // 跳转到注册或用户面板
            const target = text.includes('订阅') ? 'dashboard.html' : 'register.html';

            button.setAttribute('onclick', `window.location.href='${target}'`);
            button.addEventListener('click', (e) => {
                e.preventDefault();
                window.location.href = target;
            });

            console.log(`✅ 按钮 ${index + 1} "${text}" 已修复 → ${target}`);
        }
    });

    // 修复4：所有"免费开始使用"按钮
    const allButtons = document.querySelectorAll('button');
    allButtons.forEach((button, index) => {
        const text = button.textContent.trim();
        if (text.includes('免费开始使用')) {
            button.setAttribute('onclick', "window.location.href='register.html'");
            button.addEventListener('click', (e) => {
                e.preventDefault();
                window.location.href = 'register.html';
            });
            console.log(`✅ 免费"按钮 ${index + 1} 已修复`);
        }
    });

    console.log('');
    console.log('=== 修复完成 ===');
    console.log('现在点击任何"开始使用"按钮都会跳转到注册页面');
    console.log('如果需要用户面板，点击"订阅"按钮');
})();
