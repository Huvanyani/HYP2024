import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, BatchNormalization, Dropout
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import EarlyStopping
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import KFold
from sklearn.datasets import fetch_lfw_people


class Convnet:
    def __init__(self, img_size=(100, 100)):
        self.img_size = img_size

    def load_lfw_data(self):
        # Loads Labeled Faces in the Wild (LFW) dataset for face recognition training.

        lfw_people = fetch_lfw_people(min_faces_per_person=100, resize=0.4)
        images = lfw_people.images
        labels = lfw_people.target
        label_names = lfw_people.target_names

        # Normalizing the images
        images = images.reshape(-1, self.img_size[0], self.img_size[1], 1) / 255.0

        return images, labels, label_names

    def build_cnn_model(self, input_shape, num_classes):
        #   Building a CNN model for face encoding using keras sequential
        model = Sequential()

        # Convolutional layers with max pooling and batch normalization
        model.add(Conv2D(32, (3, 3), activation='relu', input_shape=input_shape))
        model.add(MaxPooling2D((2, 2)))
        model.add(BatchNormalization())

        model.add(Conv2D(64, (3, 3), activation='relu'))
        model.add(MaxPooling2D((2, 2)))
        model.add(BatchNormalization())

        model.add(Conv2D(128, (3, 3), activation='relu'))
        model.add(MaxPooling2D((2, 2)))
        model.add(BatchNormalization())

        # Flatten and fully connected layers with dropout
        model.add(Flatten())
        model.add(Dense(256, activation='relu'))
        model.add(Dropout(0.5))  # Dropout for regularization
        model.add(Dense(num_classes, activation='softmax'))  # Output layer for classification

        # Compiling the model
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

        return model

    @staticmethod
    def train_model(model, images, labels, epochs=20):
        # Training the CNN model with data augmentation, early stopping, and returning the training history.

        # Data augmentation
        datagen = ImageDataGenerator(
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )

        # List to store history for all folds
        history_list = []

        # Cross-validation (K-Fold)
        kfold = KFold(n_splits=5, shuffle=True, random_state=5)
        for fold, (train_idx, val_idx) in enumerate(kfold.split(images)):
            print(f"Training on fold {fold + 1}...")

            # Training data
            X_train, X_val = images[train_idx], images[val_idx]
            y_train, y_val = labels[train_idx], labels[val_idx]

            # Augmenting the training data
            datagen.fit(X_train)

            # Early stopping
            early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

            # Train the model and save the history
            history = model.fit(datagen.flow(X_train, y_train, batch_size=32),
                                validation_data=(X_val, y_val),
                                epochs=epochs,
                                callbacks=[early_stopping])

            # Appending history of each fold
            history_list.append(history.history)

        # Saving the model after the last fold
        model.save('cnn_model.h5')
        print(f"Final model saved")

        return history_list


def plot_history(history_list):
    # Plots the training and validation accuracy and loss for each fold.

    # Create pandas dataframes for the training history
    history_df = pd.DataFrame()

    # Combine history from all folds
    for fold, history in enumerate(history_list):
        fold_df = pd.DataFrame(history)
        fold_df['fold'] = fold + 1
        history_df = pd.concat([history_df, fold_df])

    # Plot training & validation accuracy values
    plt.figure(figsize=(14, 6))
    plt.subplot(1, 2, 1)
    for fold in history_df['fold'].unique():
        fold_data = history_df[history_df['fold'] == fold]
        plt.plot(fold_data['accuracy'], label=f'Train Fold {fold}')
        plt.plot(fold_data['val_accuracy'], '--', label=f'Val Fold {fold}')

    plt.title('Model Accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend()

    # Plot training & validation loss values
    plt.subplot(1, 2, 2)
    for fold in history_df['fold'].unique():
        fold_data = history_df[history_df['fold'] == fold]
        plt.plot(fold_data['loss'], label=f'Train Fold {fold}')
        plt.plot(fold_data['val_loss'], '--', label=f'Val Fold {fold}')

    plt.title('Model Loss')
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend()

    plt.show()


def main():
    # Initializing the convnet class
    convnet = Convnet()

    # Step 1: Load LFW data
    print("Loading LFW data...")
    images, labels, label_names = convnet.load_lfw_data()

    # Step 2: Build CNN model
    input_shape = (images.shape[1], images.shape[2], images.shape[3])
    num_classes = len(label_names)
    cnn_model = convnet.build_cnn_model(input_shape, num_classes)

    # Step 3: Train the CNN model with augmentation and cross-validation
    print("Training model...")
    history_list = convnet.train_model(cnn_model, images, labels, epochs=20)

    # Step 4: Plot the training and validation performance
    print("Plotting training and validation performance...")
    plot_history(history_list)


if __name__ == "__main__":
    main()
