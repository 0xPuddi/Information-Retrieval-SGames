async function getFormDataAndSubmit() {
	const ueForm = document.getElementById('ue-form');
	const ueFormData = new FormData(ueForm);
	const ueFormJson = Object.fromEntries(ueFormData.entries());

	const susForm = document.getElementById('sus-form');
	const susFormData = new FormData(susForm);
	const susFormJson = Object.fromEntries(susFormData.entries());

	const usabilityForm = document.getElementById('usability-form');
	const usabilityFormData = new FormData(usabilityForm);
	const usabilityFormJson = Object.fromEntries(usabilityFormData.entries());

	// from clinet.js
	let success = await submitFeedback({
		...ueFormJson,
		...susFormJson,
		...usabilityFormJson,
	});

	if (success) {
		const feedback_message = document.getElementById('feedback_message');
		feedback_message.innerHTML = `
			<p class="text-green-400">Feedback submitted succesfully!</p>
		`;
	}
}
