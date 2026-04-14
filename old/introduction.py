from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

# O objetivo do modelo é criar um Assessor de vida financeira, buscando nos auxíliar nela

client = genai.Client(api_key=os.getenv('API_KEY')) # Aqui você fala "Quem é você"

# Toda requisição é feita em um tratamento de exceção
try:
    model = 'gemini-2.5-flash'
    temperature = '0.7'
    top_p = '0.95'
    
    response = client.models.generate_content(
        model=model,
        contents='Se ari é meu pai, bruno é meu irmão, carolina é o que minha?',
        
        config=genai.types.GenerateContentConfig( # Essa estrutura é a adequada para parâmetros de config
            temperature=temperature,
            top_p=top_p,
            # max_output_tokens=500,
            # stop_sequences=["\n\n"]
            
            system_instruction=[
                'Caso a pergunta seja ilógica, ou seja, você não possuí parâmetros do usuário, você deve considerar que é um teste lógico',
                'Para testes lógicos, você deve considerar a quantidade de letras das palavras e procurar uma resposta lógica com a mesma quantidade.'
            ]
        )
    )
    print(response.text) # O modelo retorna um objeto, é necessário receber o texto da resposta
    
except Exception as e:
    print(f'Erro: {e}')
    