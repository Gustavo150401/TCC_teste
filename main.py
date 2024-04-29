from kivymd.app import MDApp
from kivymd.uix.screen import Screen
from kivymd.uix.button import MDRectangleFlatButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.lang import Builder
import cv2
import mediapipe as mp
import pygame

pygame.mixer.init()
audio_C = pygame.mixer.Sound('audio_C.mp3')
audio_Am = pygame.mixer.Sound('audio_Am.mp3')
audio_Bm = pygame.mixer.Sound('audio_Bm.mp3')
all_audios = (audio_C, audio_Am, audio_Bm)
video = cv2.VideoCapture(0)
hand = mp.solutions.hands
Hand = hand.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

username_helper = """
MDTextField:
    hint_text: "Enter username"
    helper_text: "or click on forgot username"
    helper_text_mode: "on_focus"
    icon_right: "android"
    icon_right_color: app.theme_cls.primary_color
    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
    size_hint_x: None
    width: 300
"""
class DemoApp(MDApp):
    def build(self):
        screen = Screen()
        self.theme_cls.theme_style='Dark'
        self.theme_cls.primary_palette = 'Blue'
        button = MDRectangleFlatButton(text='Play',pos_hint={'center_x':0.5,'center_y':0.4},
                                       on_release=self.show_data)
        self.username = Builder.load_string(username_helper)
        screen.add_widget(self.username)
        screen.add_widget(button)
        return screen
    def show_data(self,obj):
        if self.username.text is "":
            check_string = 'Please enter a username'
        else:
            check_string = self.username.text + ', Your Welcome!'
        close_button = MDFlatButton(text='Close', on_release=self.close_dialog)
        camera_button = MDFlatButton(text='Camera', on_release=self.open_camera)
        self.dialog = MDDialog(title='Username Check', text=check_string,
                          size_hint=(0.7,1),
                          buttons=[close_button,camera_button])
        self.dialog.open()
    def close_dialog(self,obj):
        self.dialog.dismiss()
        print(self.username.text)
    def open_camera(self, obj):
        try:
            current_audio = None
            while True:
                check, img = video.read()
                if not check:
                    break
                img = cv2.flip(img, 1)
                imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = Hand.process(imgRGB)
                handsPoints = results.multi_hand_landmarks
                h, w, _ = img.shape

                if handsPoints:
                    for points in handsPoints:
                        mpDraw.draw_landmarks(img, points, hand.HAND_CONNECTIONS)
                        dots = []
                        for id, cord in enumerate(points.landmark):
                            cx, cy = int(cord.x * w), int(cord.y * h)
                            cv2.putText(img, str(id), (cx, cy + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0, 2))
                            dots.append((cx, cy))
                            x_min = min(p[0] for p in dots)
                            y_min = min(p[1] for p in dots)
                            x_max = max(p[0] for p in dots)
                            y_max = max(p[1] for p in dots)
                        cv2.rectangle(img, (x_min - 20, y_min - 20), (x_max + 20, y_max + 20), (0, 255, 0), 2)

                    notas = ""
                    if points:                                                              #MApeamento POINTS
                        if (dots[8][1] < dots[6][1] and dots[12][1] > dots[10][1] and       #Condição Mapeamento
                                dots[16][1] > dots[14][1] and dots[20][1] > dots[18][1] and #encontrar maneira de otimizar por matriz
                                dots[4][0] > dots[2][0] and dots[9][1] < dots[0][1]):
                            notas = " C"                                                    #Cifra do audio
                            if current_audio != audio_C:                                    #audio atual tocando
                                current_audio = audio_C                                     #receba a tonalidade Dó
                                for audios in (audio_Am, audio_Bm):
                                    audios.stop()                                           #pare todos os outros
                                audio_C.play()                                              #reproduza esse
                        elif (dots[8][1] < dots[6][1] and dots[12][1] < dots[10][1] and
                              dots[16][1] < dots[14][1] and dots[20][1] > dots[18][1] and
                              dots[4][0] < dots[3][0] and dots[9][1] > dots[0][1]):
                            notas = "Am"
                            if current_audio != audio_Am:
                                current_audio = audio_Am
                                for audios in (audio_C, audio_Bm):
                                    audios.stop()
                                audio_Am.play()
                        elif (dots[8][1] < dots[6][1] and dots[12][1] < dots[10][1] and
                              dots[16][1] < dots[14][1] and dots[20][1] > dots[18][1] and
                              dots[4][0] > dots[3][0] and dots[9][1] > dots[0][1]):
                            notas = "Bm"
                            if current_audio != audio_Bm:
                                current_audio = audio_Bm
                                for audios in (audio_Am, audio_C):
                                    audios.stop()
                                audio_Bm.play()
                    cv2.putText(img, str(notas), (x_min - 30, y_min - 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2,
                                (255, 255, 255), 2)
                else:
                    for audios in all_audios:
                        audios.stop()
                cv2.imshow("Imagem", img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
        finally:
            Hand.close()
            video.release()
            cv2.destroyAllWindows()

DemoApp().run()