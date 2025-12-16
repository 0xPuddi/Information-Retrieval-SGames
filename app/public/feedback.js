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

	// radius for tasks
	const flappyBirdStatus = usabilityForm.querySelector(
		'input[name="task_flappy_bird_completed"]:checked',
	)?.value;
	usabilityFormJson['task_flappy_bird_completed'] = flappyBirdStatus;

	const albionOnlineStatus = usabilityForm.querySelector(
		'input[name="task_albion_online_completed"]:checked',
	)?.value;
	usabilityFormJson['task_albion_online_completed'] = albionOnlineStatus;

	const organizedTheftStatus = usabilityForm.querySelector(
		'input[name="task_organized_theft_completed"]:checked',
	)?.value;
	usabilityFormJson['task_organized_theft_completed'] = organizedTheftStatus;

	const eldenRingStatus = usabilityForm.querySelector(
		'input[name="task_elden_ring_completed"]:checked',
	)?.value;
	usabilityFormJson['task_elden_ring_completed'] = eldenRingStatus;

	const freeSearchStatus = usabilityForm.querySelector(
		'input[name="task_free_search_completed"]:checked',
	)?.value;
	usabilityFormJson['task_free_search_completed'] = freeSearchStatus;

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
