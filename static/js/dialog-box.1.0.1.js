class DialogBox {

	constructor({

        titleText = 'Error',
		messageText = 'Something unexpected has gone wrong. If the problem persists, contact your administrator',
		trueButtonText = 'OK',
		falseButtonText = null,
		neutralButtonText = null,

	} = {}) {

		this.titleText = titleText;
		this.messageText = messageText;
		this.trueButtonText = trueButtonText;
		this.falseButtonText = falseButtonText;
		this.neutralButtonText = neutralButtonText;

		this.hasFalse = falseButtonText != null;
		this.hasNeutral = neutralButtonText != null;

		this.dialog = undefined;
		this.trueButton = undefined;
		this.falseButton = undefined;
        this.neutralButton = undefined;
        
		this.parent = document.body;

		this._createDialog(this);
		this._appendDialog();

	}

	_createDialog(context) {

		this.dialog = document.createElement("div");
		this.dialog.classList.add("dialog-box");

		this.dialog.style.opacity = 0;

		const title = document.createElement("h3");
		title.textContent = this.titleText;
		title.classList.add("dialog-box-title");
		this.dialog.appendChild(title);

		const question = document.createElement("h4");
		question.textContent = this.messageText;
		question.classList.add("dialog-box-message");
		this.dialog.appendChild(question);

		const buttonContainer = document.createElement('div');
		buttonContainer.classList.add('dialog-box-button-container');
		this.dialog.appendChild(buttonContainer);

		this.trueButton = document.createElement("a");
		this.trueButton.classList.add(
			"dialog-box-button",
			"dialog-box-button--true"
		);
		this.trueButton.textContent = this.trueButtonText;
		this.trueButton.addEventListener('click', function() {
			context._destroy();
		});
		buttonContainer.appendChild(this.trueButton);

		if (this.hasFalse) {
			this.falseButton = document.createElement("a");
			this.falseButton.classList.add(
				"dialog-box-button",
				"dialog-box-button--false"
			);
			this.falseButton.textContent = this.falseButtonText;
			this.falseButton.addEventListener('click', function() {
				context._destroy();
			});
			buttonContainer.appendChild(this.falseButton);
		}

		if (this.hasNeutral) {
			this.neutralButton = document.createElement("a");
			this.neutralButton.classList.add(
				"dialog-box-button",
				"dialog-box-button--neutral"
			);
			this.neutralButton.textContent = this.neutralButtonText;
			this.neutralButton.addEventListener('click', function() {
				context._destroy();
			});
			buttonContainer.appendChild(this.neutralButton);
		}

	}

	_appendDialog() {
		const diag = this.dialog;
		this.parent.appendChild(diag);
		setTimeout(function(){
			diag.style.opacity = 1;
		}, 0);
	}

	_destroy() {
		this.parent.removeChild(this.dialog);
		delete this;
	}

	respond() {
		return new Promise((resolve, reject) => {

			const somethingWentWrongUponCreation = !this.dialog || !this.trueButton;

			if (somethingWentWrongUponCreation) {
				reject("Something went wrong upon modal creation");
			}

			this.trueButton.addEventListener("click", () => {
				resolve(true);
			});

			if (this.hasFalse) {
				this.falseButton.addEventListener("click", () => {
					resolve(false);
				});
			}

		});
	}

}