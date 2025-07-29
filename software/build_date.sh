#!/bin/bash
echo ";From here it is generated and pushed by update_build.sh"  > build_date.inc
echo "BUILD_DATE:" >> monitor.asm >> build_date.inc
#echo '              DC.B "Build: '"$(date +'%Y-%m-%d %H:%M:%S')"'",13,10' >> build_date.inc
# Extrai cada componente da data e soma tudo
YEAR=$(date +'%Y')     # Ano (4 dígitos)
MONTH=$(date +'%m')    # Mês (01-12)
DAY=$(date +'%d')      # Dia (01-31)
HOUR=$(date +'%H')     # Hora (00-23)
MIN=$(date +'%M')      # Minuto (00-59)
SEC=$(date +'%S')      # Segundo (00-59)

# Calcula a soma (remove zeros à esquerda para evitar octal)
TOTAL=$((10#$YEAR + 10#$MONTH + 10#$DAY + 10#$HOUR + 10#$MIN + 10#$SEC))

# Gera o arquivo .asm com a string e a soma
echo '      DC.B "Build.: '"$(date +'%Y-%m-%d %H:%M:%S')"'",13,10' >> build_date.inc
echo '      DC.B "Serial: '$DAY$TOTAL'",0' >> build_date.inc
echo ";End generated code" >> build_date.inc
