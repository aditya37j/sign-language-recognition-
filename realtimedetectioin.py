# from keras.models import model_from_json
# import cv2
# import numpy as np

# json_file = open("signlanguagedetectionmodel.json", "r")
# model_json = json_file.read()
# json_file.close()
# model = model_from_json(model_json)
# model.load_weights("signlanguagedetectionmodel.h5")

# def extract_features(image):
#     feature = np.array(image)
#     feature = feature.reshape(1,48,48,1)
#     return feature/255.0

# cap = cv2.VideoCapture(0)
# label = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'blank']
# while True:
#     _,frame = cap.read()
#     cv2.rectangle(frame,(0,40),(300,300),(0, 165, 255),1)
#     cropframe=frame[40:300,0:300]
#     cropframe=cv2.cvtColor(cropframe,cv2.COLOR_BGR2GRAY)
#     cropframe = cv2.resize(cropframe,(48,48))
#     cropframe = extract_features(cropframe)
#     pred = model.predict(cropframe) 
#     prediction_label = label[pred.argmax()]
#     cv2.rectangle(frame, (0,0), (300, 40), (0, 165, 255), -1)
#     if prediction_label == 'blank':
#         cv2.putText(frame, " ", (10, 30),cv2.FONT_HERSHEY_SIMPLEX,1, (255, 255, 255),2,cv2.LINE_AA)
#     else:
#         accu = "{:.2f}".format(np.max(pred)*100)
#         cv2.putText(frame, f'{prediction_label}  {accu}%', (10, 30),cv2.FONT_HERSHEY_SIMPLEX,1, (255, 255, 255),2,cv2.LINE_AA)
#     cv2.imshow("output",frame)
#     cv2.waitKey(27)
    
# cap.release()
# cv2.destroyAllWindows()


from keras.models import model_from_json
import cv2
import numpy as np
import time

# Load the model
json_file = open("signlanguagedetectionmodel.json", "r")
model_json = json_file.read()
json_file.close()
model = model_from_json(model_json)
model.load_weights("signlanguagedetectionmodel.h5")

# Function to extract features from an image
def extract_features(image):
    feature = np.array(image)
    feature = feature.reshape(1, 48, 48, 1)
    return feature / 255.0

cap = cv2.VideoCapture(0)
label = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'blank']

# Variables to track sentence, spaces, and full stops
sentence = ""
space_start_time = None
fullstop_start_time = None

while True:
    _, frame = cap.read()
    cv2.rectangle(frame, (0, 40), (300, 300), (0, 165, 255), 1)
    cropframe = frame[40:300, 0:300]
    cropframe = cv2.cvtColor(cropframe, cv2.COLOR_BGR2GRAY)
    cropframe = cv2.resize(cropframe, (48, 48))
    cropframe = extract_features(cropframe)
    pred = model.predict(cropframe)
    prediction_label = label[pred.argmax()]

    cv2.rectangle(frame, (0, 0), (300, 40), (0, 165, 255), -1)
    if prediction_label == 'blank':
        current_time = time.time()

        if space_start_time is None:
            space_start_time = current_time
        if fullstop_start_time is None:
            fullstop_start_time = current_time

        # Check for full stop
        if current_time - fullstop_start_time > 7:
            if sentence and not sentence.endswith(". "):
                sentence += ". "
            fullstop_start_time = None
            space_start_time = None
        # Check for space between words
        elif current_time - space_start_time > 2:
            if sentence and not sentence.endswith(" "):
                sentence += " "
            space_start_time = None

        cv2.putText(frame, " ", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    else:
        fullstop_start_time = None
        space_start_time = None
        accu = "{:.2f}".format(np.max(pred) * 100)
        cv2.putText(frame, f'{prediction_label}  {accu}%', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

        # Add character to sentence
        sentence += prediction_label

    # Display the sentence on a separate frame
    sentence_frame = np.zeros((100, 600, 3), dtype=np.uint8)
    cv2.putText(sentence_frame, sentence, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    # Show frames
    cv2.imshow("output", frame)
    cv2.imshow("Sentence", sentence_frame)

    if cv2.waitKey(27) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
