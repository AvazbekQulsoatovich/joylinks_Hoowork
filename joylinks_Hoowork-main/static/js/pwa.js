// PWA Installation Logic
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent Chrome 67 and earlier from automatically showing the prompt
    e.preventDefault();
    // Stash the event so it can be triggered later.
    deferredPrompt = e;

    // Show the install button if it exists
    const installBtns = document.querySelectorAll('.pwa-install-btn');
    installBtns.forEach(btn => btn.style.display = 'flex');
});

async function installPWA() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        console.log(`User response to the install prompt: ${outcome}`);
        deferredPrompt = null;
    } else {
        // Fallback or instructions
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        const isSecure = window.isSecureContext;

        if (isIOS) {
            showIOSModal();
        } else {
            if (!isSecure && window.location.hostname !== 'localhost') {
                alert("Ilovani o'rnatish uchun xavfsiz bog'lanish (HTTPS) zarur. \n\nHozircha ilovani 'Bosh ekranga qo'shish' (Add to home screen) orqali qo'lda o'rnatishingiz mumkin.");
            } else {
                alert("Ilovani o'rnatish uchun:\n1. Brauzer menyusini oching (uchta nuqta)\n2. 'Ilovani o'rnatish' yoki 'Bosh ekranga qo'shish' tugmasini bosing.");
            }
        }
    }
}

function showIOSModal() {
    const modal = document.getElementById('ios-install-modal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

function closeIOSModal() {
    const modal = document.getElementById('ios-install-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Add event listeners to all install buttons
    document.querySelectorAll('.pwa-install-btn').forEach(btn => {
        btn.addEventListener('click', installPWA);
    });

    document.querySelectorAll('.ios-install-info-btn').forEach(btn => {
        btn.addEventListener('click', showIOSModal);
    });

    document.querySelectorAll('.modal-close, .close-modal').forEach(btn => {
        btn.addEventListener('click', closeIOSModal);
    });

    // Close modal on outside click
    window.addEventListener('click', (e) => {
        const modal = document.getElementById('ios-install-modal');
        if (e.target === modal) {
            closeIOSModal();
        }
    });
});
