# Preprocessing
## 1. Data Preparation
*   **Manual Download**: Download the dataset and rename the archive to `chexpert.zip`.
    *   **Google Colab**: Place `chexpert.zip` in the root directory of your Colab environment.
    *   **Local Machine**: Place `chexpert.zip` in the same folder as the preprocessing scripts.
*   **Kaggle API**: Use the Kaggle API to download the dataset directly.
    - Not runable on colab.

## 2. Python environment 
- Run `pip install -r requirement.txt`

## 3. Output Variables for training the module using Pytorch
- Training Data: `train_dataset`, `train_loader`, `train_images`, `train_labels`
- Validation Data: `validation_dataset`, `validation_loader`, `validation_images`, `validation_labels`
- Test Data: `test_dataset`, `test_loader`, `test_images`, `test_labels`

