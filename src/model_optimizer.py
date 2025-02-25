# model_optimizer.py
from typing import Optional
import torch
import numpy as np
from src.file_manager import FileManager

class ModelOptimizer:
    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager

    def quantize_model(self, model_path: str, bits: int = 8) -> Optional[str]:
        """Cuantiza un modelo a una precisión específica (8 o 16 bits)."""
        try:
            if bits not in [8, 16]:
                raise ValueError("La cuantización solo admite 8 o 16 bits")

            # Cargar el modelo
            model = torch.load(model_path)

            # Cuantizar el modelo
            with torch.no_grad():
                # Convertir a int8 o float16 según los bits especificados
                dtype = torch.int8 if bits == 8 else torch.float16
                for param in model.parameters():
                    param.data = param.data.to(dtype)

            # Guardar el modelo cuantizado
            quantized_path = model_path.replace('.pt', f'_quantized_{bits}bit.pt')
            torch.save(model, quantized_path)

            # Comprimir y subir el modelo cuantizado
            return await self.file_manager.subir_archivo(quantized_path)

        except Exception as e:
            print(f"Error al cuantizar el modelo: {str(e)}")
            return None

    def prune_model(self, model_path: str, threshold: float = 0.1) -> Optional[str]:
        """Aplica pruning al modelo eliminando pesos por debajo del umbral."""
        try:
            # Cargar el modelo
            model = torch.load(model_path)

            # Aplicar pruning
            with torch.no_grad():
                for param in model.parameters():
                    mask = torch.abs(param.data) > threshold
                    param.data *= mask

            # Guardar el modelo podado
            pruned_path = model_path.replace('.pt', f'_pruned_{threshold}.pt')
            torch.save(model, pruned_path)

            # Comprimir y subir el modelo podado
            return await self.file_manager.subir_archivo(pruned_path)

        except Exception as e:
            print(f"Error al podar el modelo: {str(e)}")
            return None

    def compress_model(self, model_path: str) -> Optional[str]:
        """Comprime el modelo usando el FileManager existente."""
        try:
            return await self.file_manager.subir_archivo(model_path)
        except Exception as e:
            print(f"Error al comprimir el modelo: {str(e)}")
            return None

    async def download_model(self, url: str, destination: str) -> bool:
        """Descarga un modelo desde la URL proporcionada."""
        return self.file_manager.descargar_archivo(url, destination)