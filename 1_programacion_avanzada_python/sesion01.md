# Sesión 1 — Entornos virtuales y Git

## 1. Diferencia entre Python global y `.venv`
El Python global es el Python instaldado en el ordenador y que puede ser utilizado por distintos proyectos. Un .venv es un entorno virtual aislado para un proyecto en concreto que tiene sus propias librerías y dependencias. Así cada proyecto puede tener las versiones que necesita sin que se creen conflictos con otros proyectos.

## 2. ¿Para qué sirve `python -m pip` frente a llamar solo a `pip`?

Si usamos python -m pip evitamos instalar una librería en un Python distinto al de nuestro entorno virtual, ya que si solo usamos pip si tenemos varios python instalados puede usar uno distinto al que quieres.

## 3. Explica working tree / staging / commit

El working tree se refiere a los archivos que estas modificando, cuando eliges los cambios que quieres incluir en el próximo commit pasando al staging (usas para esto git add) y commit es ya la versión guardada con los cambios.

## 4. ¿Clone y pull son lo mismo? ¿Por qué?
Git clone se usa cuando se quiere descargar un repositorio por primera vez al ordenador. Git pull se utiliza cuando ya tienes el repositorio y lo que quieres es traer los cambios que hayan en el repositorio remoto al ordenador.

## 5. Lista cuatro cosas que no se suben a GitHub y justifica una
No se suben .venv/, .env. , carpetas como __pycache__ o archivos temporales como .vscode/. 
No se sube .env porque puede tener información sensible como claves API o contraseñas y si se publican en Github, otras personas podrían acceder a esas credenciales y utilizarlas.

## 6. Reescribe a buen estilo estos commits:
- `update` -- Update README
- `fix final` -- Fix ejercicio1
- `cambios varios`-- Update requirements and .gitignore

## 7. ¿Qué haces si el IDE no importa `pandas` pero la terminal sí?
Esto puede ser porque puede ser que el IDE este utilizando un Python distinto al del entorno virtual, lo que habría que hacer es seleccionar el intérprete de python que este dentro de .venv.

## 8. ¿Qué haces si subiste `.env` por error?
Si se sube .env por error, lo primero que habría que hacer es revocar o cambiar las claves que hubiera dentro para que dejen de ser válidas.
Después haría que git dejara de trackear el archivo con git rm --cached .env y añadiría .env a .gitignore.
