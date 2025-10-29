"""
Utilitários para conversão de timezone UTC para Brasília
"""
from datetime import datetime
import pytz


class TimezoneConverter:
    """Converte horários entre timezones"""
    
    BRASILIA_TZ = pytz.timezone('America/Sao_Paulo')
    UTC_TZ = pytz.UTC
    
    @staticmethod
    def utc_to_brasilia(utc_timestamp: int) -> datetime:
        """
        Converte timestamp UTC para horário de Brasília
        
        Args:
            utc_timestamp: Timestamp em segundos (Unix time)
            
        Returns:
            datetime em horário de Brasília
        """
        # Criar datetime UTC
        utc_dt = datetime.fromtimestamp(utc_timestamp, tz=TimezoneConverter.UTC_TZ)
        
        # Converter para Brasília
        brasilia_dt = utc_dt.astimezone(TimezoneConverter.BRASILIA_TZ)
        
        return brasilia_dt
    
    @staticmethod
    def format_brasilia_time(utc_timestamp: int, format_str: str = "%d/%m/%Y %H:%M") -> str:
        """
        Formata horário em Brasília
        
        Args:
            utc_timestamp: Timestamp em segundos
            format_str: Formato desejado
            
        Returns:
            String formatada
        """
        brasilia_dt = TimezoneConverter.utc_to_brasilia(utc_timestamp)
        return brasilia_dt.strftime(format_str)
    
    @staticmethod
    def get_brasilia_now() -> datetime:
        """Retorna horário atual em Brasília"""
        return datetime.now(TimezoneConverter.BRASILIA_TZ)
    
    @staticmethod
    def is_match_today(utc_timestamp: int) -> bool:
        """Verifica se o match é hoje em Brasília"""
        match_time = TimezoneConverter.utc_to_brasilia(utc_timestamp)
        today = TimezoneConverter.get_brasilia_now().date()
        return match_time.date() == today
    
    @staticmethod
    def is_match_tomorrow(utc_timestamp: int) -> bool:
        """Verifica se o match é amanhã em Brasília"""
        match_time = TimezoneConverter.utc_to_brasilia(utc_timestamp)
        tomorrow = (TimezoneConverter.get_brasilia_now().date() + 
                   pytz.timezone('America/Sao_Paulo').localize(datetime.now()).timedelta(days=1)).date()
        return match_time.date() == tomorrow
    
    @staticmethod
    def get_match_status(utc_timestamp: int) -> str:
        """
        Obtém status do match (HOJE, AMANHÃ, PRÓXIMO, PASSADO)
        
        Args:
            utc_timestamp: Timestamp em segundos
            
        Returns:
            Status do match
        """
        match_time = TimezoneConverter.utc_to_brasilia(utc_timestamp)
        now = TimezoneConverter.get_brasilia_now()
        
        if match_time.date() == now.date():
            return "🔴 HOJE"
        elif match_time.date() > now.date():
            days_diff = (match_time.date() - now.date()).days
            if days_diff == 1:
                return "🟡 AMANHÃ"
            elif days_diff <= 7:
                return f"🟢 {days_diff}d"
            else:
                return "⏰ PRÓXIMO"
        else:
            return "⚫ PASSADO"
    
    @staticmethod
    def get_time_until_match(utc_timestamp: int) -> str:
        """
        Calcula tempo até o match
        
        Args:
            utc_timestamp: Timestamp em segundos
            
        Returns:
            String com tempo até o match
        """
        match_time = TimezoneConverter.utc_to_brasilia(utc_timestamp)
        now = TimezoneConverter.get_brasilia_now()
        
        if match_time <= now:
            return "Jogo iniciado"
        
        diff = match_time - now
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        days = diff.days
        
        if days > 0:
            return f"{days}d {hours}h"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    @staticmethod
    def format_brasilia_time_short(utc_timestamp: int) -> str:
        """
        Formata horário em Brasília (formato curto)
        
        Args:
            utc_timestamp: Timestamp em segundos
            
        Returns:
            String formatada (HH:MM)
        """
        return TimezoneConverter.format_brasilia_time(utc_timestamp, "%H:%M")
    
    @staticmethod
    def format_brasilia_date_short(utc_timestamp: int) -> str:
        """
        Formata data em Brasília (formato curto)
        
        Args:
            utc_timestamp: Timestamp em segundos
            
        Returns:
            String formatada (DD/MM)
        """
        return TimezoneConverter.format_brasilia_time(utc_timestamp, "%d/%m")
    
    @staticmethod
    def format_brasilia_full(utc_timestamp: int) -> str:
        """
        Formata horário completo em Brasília
        
        Args:
            utc_timestamp: Timestamp em segundos
            
        Returns:
            String formatada (DD/MM/YYYY HH:MM)
        """
        return TimezoneConverter.format_brasilia_time(utc_timestamp, "%d/%m/%Y %H:%M")
    
    @staticmethod
    def get_weekday_name(utc_timestamp: int) -> str:
        """
        Obtém nome do dia da semana em português
        
        Args:
            utc_timestamp: Timestamp em segundos
            
        Returns:
            Nome do dia da semana
        """
        weekdays = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        match_time = TimezoneConverter.utc_to_brasilia(utc_timestamp)
        return weekdays[match_time.weekday()]
    
    @staticmethod
    def format_brasilia_with_weekday(utc_timestamp: int) -> str:
        """
        Formata horário com dia da semana
        
        Args:
            utc_timestamp: Timestamp em segundos
            
        Returns:
            String formatada (Dia, DD/MM HH:MM)
        """
        weekday = TimezoneConverter.get_weekday_name(utc_timestamp)
        date_time = TimezoneConverter.format_brasilia_time(utc_timestamp, "%d/%m %H:%M")
        return f"{weekday}, {date_time}"


# Exemplo de uso
if __name__ == "__main__":
    import time
    
    # Timestamp de exemplo (29/10/2025 20:30 UTC)
    utc_timestamp = int(time.time()) + 86400  # Próximo dia
    
    print("Conversão de Timezone UTC para Brasília")
    print("=" * 50)
    print()
    
    print(f"Timestamp: {utc_timestamp}")
    print(f"Horário Brasília: {TimezoneConverter.format_brasilia_full(utc_timestamp)}")
    print(f"Horário Brasília (curto): {TimezoneConverter.format_brasilia_time_short(utc_timestamp)}")
    print(f"Data Brasília: {TimezoneConverter.format_brasilia_date_short(utc_timestamp)}")
    print(f"Com dia da semana: {TimezoneConverter.format_brasilia_with_weekday(utc_timestamp)}")
    print()
    
    print(f"Status do match: {TimezoneConverter.get_match_status(utc_timestamp)}")
    print(f"Tempo até o match: {TimezoneConverter.get_time_until_match(utc_timestamp)}")
    print(f"É hoje? {TimezoneConverter.is_match_today(utc_timestamp)}")
    print(f"É amanhã? {TimezoneConverter.is_match_tomorrow(utc_timestamp)}")