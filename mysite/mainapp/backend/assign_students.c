# i n c l u d e   " a s s i g n _ s t u d e n t s . h " 
 
 i n t   *   a s s i g n _ s t u d e n t s ( s t r u c t   d o m a i n   *   D ,   i n t   t o t a l ,   i n t   l e a d e r s ,   i n t   t i m e s ,   i n t   *   g e n d e r s ,   s t r u c t   d o m a i n   *   b i n _ c o n s t r a i n t s ,   i n t   m a x _ s e c o n d s ) { 
         s t r u c t   a s s i g n m e n t   *   a   =   i n i t i a l i z e _ a s s i g n m e n t ( t o t a l ,   l e a d e r s ,   t i m e s ,   g e n d e r s ,   b i n _ c o n s t r a i n t s ) ; 
         i n t   *   r e s u l t   =   ( i n t   * )   m a l l o c ( t o t a l   *   s i z e o f ( i n t ) ) ; 
         i n t   i ; 
         f o r   ( i   =   0 ;   i   <   t o t a l ;   i + + ) { 
                 * ( r e s u l t   +   i )   =   - 1 ; 
         } 
         i n t   s t a t u s   =   b a c k t r a c k i n g _ s e a r c h ( a ,   D ,   r e s u l t ,   m a x _ s e c o n d s ) ; 
         f r e e _ a s s i g n m e n t ( a ) ; 
         r e t u r n   r e s u l t ; 
 } 
 