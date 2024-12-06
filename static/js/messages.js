const motivationalMessages = [
    // Health & Wellness
    "Each breath is a new beginning.",
    "今日から新しい人生 (Today begins a new life)",
    "Your lungs are healing with each smoke-free moment.",
    "Every 'no' to a cigarette is a 'yes' to life.",
    "Small steps lead to big changes.",
    "一期一会 (One life, one moment)",
    "Your body thanks you for every cigarette you don't smoke.",
    "Breathe in strength, breathe out weakness.",
    
    // Mindfulness & Present Moment
    "This moment is your moment of change.",
    "Focus on now, not the craving.",
    "禅 - Find peace in the present moment.",
    "The craving will pass, but your strength will last.",
    "Mindful breathing leads to mindful living.",
    "Each moment of resistance builds your power.",
    "Peace comes from within, not from cigarettes.",
    "Be present, be strong, be free.",
    
    // Progress & Achievement
    "Every day without smoking is a victory.",
    "You're stronger than you think.",
    "進歩 - Progress is made one step at a time.",
    "Yesterday's choices brought you here; today's choices take you forward.",
    "Your journey of a thousand miles began with a single step.",
    "Each day brings new strength and new thoughts.",
    "Success is built one moment at a time.",
    "You're writing your success story right now.",
    
    // Financial Wisdom
    "Save money, save life.",
    "投資 - Invest in your health.",
    "Your wallet grows as your habits improve.",
    "Health is wealth, literally.",
    "Every unsmoked cigarette is money saved.",
    "Invest in yourself, not in cigarettes.",
    "Your future self thanks you for saving.",
    "Financial freedom starts with breaking free.",
    
    // Personal Power
    "You are the master of your habits.",
    "意志 - Willpower grows with each resistance.",
    "Your strength is greater than any craving.",
    "You choose your path forward.",
    "Every 'no' makes you stronger.",
    "You have the power to change your story.",
    "Your determination defines your destination.",
    "Be the author of your healing journey.",
    
    // Future Focus
    "Tomorrow thanks you for today's strength.",
    "未来 - Your future is bright and smoke-free.",
    "Build the tomorrow you deserve today.",
    "Your health is your greatest investment.",
    "Every smoke-free day is a gift to your future.",
    "Plant the seeds of change today.",
    "Your future self celebrates your current strength.",
    "Create the life you want to live.",
    
    // Nature & Harmony
    "Breathe with nature's rhythm.",
    "調和 - Find harmony in healthy choices.",
    "Let your lungs dance with the fresh air.",
    "Nature supports your healing journey.",
    "Feel the pure air fill your lungs.",
    "Harmony comes from healthy choices.",
    "Your body is a garden; tend it well.",
    "Flow with nature's healing power.",
    
    // Community & Support
    "You're not alone on this journey.",
    "共に - Together, we are stronger.",
    "Your success inspires others.",
    "Every step forward lights the way for someone else.",
    "Your strength builds a healthier community.",
    "Share your journey, inspire others.",
    "Your courage creates ripples of change.",
    "We rise by lifting others.",
    
    // Wisdom & Learning
    "Each craving teaches you strength.",
    "智慧 - Wisdom comes from experience.",
    "Learn from yesterday, live for today.",
    "Every challenge is a chance to grow.",
    "Your journey is your greatest teacher.",
    "Wisdom grows with every choice.",
    "Understanding yourself leads to freedom.",
    "Knowledge of self brings power of change.",
    
    // Joy & Celebration
    "Celebrate each smoke-free moment.",
    "喜び - Find joy in your progress.",
    "Your smile gets brighter every day.",
    "Freedom tastes sweeter than any cigarette.",
    "Dance with the joy of being smoke-free.",
    "Every breath is a celebration of life.",
    "Your heart sings with each healthy choice.",
    "Happiness grows as habits improve.",
    
    // Transformation
    "Transform your life one breath at a time.",
    "変化 - Change creates opportunity.",
    "Every moment is a chance to transform.",
    "You're becoming stronger every day.",
    "Watch your life transform with each choice.",
    "Change is your power.",
    "Transform your thoughts, transform your life.",
    "Every day brings new transformation."
];

function getRandomMessage() {
    return motivationalMessages[Math.floor(Math.random() * motivationalMessages.length)];
}

function updateFooterMessage() {
    const quoteElement = document.querySelector('.quote');
    if (quoteElement) {
        // Add fade-out class
        quoteElement.classList.add('fade-out');
        
        // Wait for fade-out transition
        setTimeout(() => {
            // Update message
            quoteElement.textContent = getRandomMessage();
            
            // Remove fade-out and add fade-in
            quoteElement.classList.remove('fade-out');
            quoteElement.classList.add('fade-in');
            
            // Clean up fade-in class
            setTimeout(() => {
                quoteElement.classList.remove('fade-in');
            }, 500);
        }, 500);
    }
}

// Update message every 15 seconds (increased from 10 to give more reading time)
setInterval(updateFooterMessage, 15000);

// Initial update
document.addEventListener('DOMContentLoaded', () => {
    const quoteElement = document.querySelector('.quote');
    if (quoteElement) {
        quoteElement.textContent = getRandomMessage();
        quoteElement.classList.add('fade-in');
        setTimeout(() => {
            quoteElement.classList.remove('fade-in');
        }, 500);
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.alert');
    
    messages.forEach(function(message) {
        // Add fade-out class after 4 seconds
        setTimeout(() => {
            message.classList.add('fade-out');
            // Remove the element after animation completes
            setTimeout(() => {
                message.remove();
            }, 300); // 300ms matches the animation duration
        }, 4000);
    });
});
