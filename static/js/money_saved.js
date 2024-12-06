function updateMoneySaved() {
    // Get the required values from data attributes
    const startDateStr = document.getElementById('money-saved').dataset.startDate;
    const dailyCigarettes = parseInt(document.getElementById('money-saved').dataset.dailyCigarettes);
    const costPerCigarette = parseFloat(document.getElementById('money-saved').dataset.costPerCigarette);
    const totalSmoked = parseInt(document.getElementById('money-saved').dataset.totalSmoked);
    const currencySymbol = document.getElementById('money-saved').dataset.currency;

    // Calculate days since start (including today)
    const startDate = new Date(startDateStr);
    const today = new Date();
    const daysSinceStart = Math.floor((today - startDate) / (1000 * 60 * 60 * 24)) + 1;

    // Calculate money saved
    const totalPotential = daysSinceStart * dailyCigarettes;
    const cigarettesSaved = totalPotential - totalSmoked;
    const moneySaved = (cigarettesSaved * costPerCigarette).toFixed(2);

    // Update the display
    document.getElementById('money-saved').textContent = `${currencySymbol}${moneySaved}`;
}

// Update immediately and then every minute
updateMoneySaved();
setInterval(updateMoneySaved, 60000); // 60000 ms = 1 minute
