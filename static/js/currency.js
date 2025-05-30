console.log("Currency initialization script loaded");

// Global function to set currency value with AutoNumeric support
window.setCurrencyValue = function(field, value) {
    if (!field) {
        console.warn('[Currency] No field provided to setCurrencyValue');
        return false;
    }
    
    try {
        if (typeof AutoNumeric !== 'undefined') {
            const autoNumericInstance = AutoNumeric.getAutoNumericElement(field);
            if (autoNumericInstance) {
                autoNumericInstance.set(value);
                console.log(`[Currency] Set value ${value} using AutoNumeric on field ${field.id || field.name || 'unknown'}`);
                return true;
            } else {
                // AutoNumeric not initialized on this field
                field.value = value;
                console.log(`[Currency] AutoNumeric not initialized on field ${field.id || field.name || 'unknown'}, set raw value: ${value}`);
                return false;
            }
        } else {
            // AutoNumeric not available
            field.value = value;
            console.log(`[Currency] AutoNumeric not available, set raw value ${value} on field ${field.id || field.name || 'unknown'}`);
            return false;
        }
    } catch (error) {
        console.warn(`[Currency] Error setting value on field ${field.id || field.name || 'unknown'}:`, error);
        field.value = value;
        return false;
    }
};

document.addEventListener("DOMContentLoaded", function () {
  const moneyInputs = document.querySelectorAll(".money");

  if (moneyInputs.length > 0) {
    console.log(
      `[Currency] Initializing AutoNumeric on ${moneyInputs.length} money input fields`,
    );

    moneyInputs.forEach((el) => {
      // Ensure AutoNumeric is available
      if (typeof AutoNumeric !== "undefined") {
        new AutoNumeric(el, {
          currencySymbol: "€ ", // Euro symbol with space
          currencySymbolPlacement: "p", // Prefix
          decimalCharacter: ".",
          digitGroupSeparator: ",",
          decimalPlaces: 2,
          unformatOnSubmit: true, // IMPORTANT: Sends raw number on form submit
        });
        console.log(
          `[Currency] AutoNumeric initialized on ${el.id || el.name || "unnamed input"}`,
        );
      } else {
        console.error("[Currency] AutoNumeric library not loaded.");
      }
    });
    
    console.log("[Currency] AutoNumeric initialization complete");
  } else {
    console.log("[Currency] No money inputs found on page to initialize");
  }
});
